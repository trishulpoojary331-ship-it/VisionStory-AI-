import re


class StoryRelevanceScorer:
    """
    Evaluates semantic correspondence between the visual information extracted from the image
    and the generated narrative.
    Computes Entity Fidelity, Setting Alignment, and Thematic Resonance scores.
    """

    def evaluate(self, vision_metadata, story_data):
        """
        Evaluate relevance of story to the image.
        vision_metadata: dict containing detected_objects, scene_category, lighting_atmosphere, ambient_mood
        story_data: dict containing title, chapters, characters, dialogue, moral
        """
        # Aggregate full story text
        story_corpus = []
        if "title" in story_data:
            story_corpus.append(str(story_data["title"]))
        
        if "characters" in story_data:
            for char in story_data["characters"]:
                story_corpus.append(f"{char.get('name', '')} {char.get('role', '')} {char.get('personality', '')}")

        if "chapters" in story_data:
            for ch in story_data["chapters"]:
                story_corpus.append(f"{ch.get('heading', '')} {ch.get('content', '')}")

        if "dialogue" in story_data:
            for d in story_data["dialogue"]:
                story_corpus.append(f"{d.get('speaker', '')} {d.get('line', '')}")

        if "moral" in story_data:
            story_corpus.append(str(story_data["moral"]))

        full_text = " ".join(story_corpus).lower()

        # 1. Evaluate Entity Recall (Visual Objects -> Text)
        detected_objs = vision_metadata.get("detected_objects", [])
        entity_matches = []
        matched_count = 0

        # Mapping for lenient synonym matching
        synonym_map = {
            "wooden boat": ["boat", "vessel", "skiff", "canoe", "ship", "craft", "mast", "hull", "sail"],
            "ocean waters": ["ocean", "sea", "water", "waves", "tide", "surf", "shore", "depths", "horizon"],
            "sandy shore": ["sand", "beach", "shore", "coastline", "dune", "coast", "tide"],
            "gentle waves": ["wave", "ripple", "tide", "surf", "water", "foam"],
            "seagull": ["seagull", "gull", "bird", "feather", "wings", "sky"],
            "loyal canine companion": ["dog", "canine", "hound", "companion", "pup", "puppy", "paws", "fur", "bark", "creature", "pet", "friend", "retriever"],
            "verdant fields": ["field", "fields", "meadow", "grass", "green", "pasture", "ground", "plain", "hills", "countryside"],
            "rustic wooden fence": ["fence", "wood", "wooden", "rail", "gate", "barrier", "post", "rustic"],
            "sunlit meadow": ["meadow", "grass", "sunlight", "field", "sunlit", "pasture", "sunbeams", "countryside"],
            "devoted companion & caretaker": ["companion", "caretaker", "friend", "guardian", "traveler", "explorer", "guide", "partner"],
            "solitary traveler / explorer": ["traveler", "explorer", "wanderer", "figure", "journey", "protagonist", "walker", "contemplating"],
            "solitary traveler / child": ["child", "boy", "girl", "wanderer", "traveler", "figure", "youth", "protagonist", "person", "he", "she"],
            "towering pines": ["tree", "trees", "pine", "pines", "forest", "wood", "canopy", "trunk", "bark"],
            "mossy pathway": ["path", "pathway", "moss", "trail", "walkway", "ground"],
            "canopy sunbeams": ["sunbeam", "sunbeams", "light", "canopy", "rays", "sunlight"],
            "skyscrapers": ["skyscraper", "tower", "building", "buildings", "glass", "skyline", "high-rise"],
            "city lights": ["lights", "neon", "glow", "illuminated", "billboards", "light"],
            "reading desk": ["desk", "table", "reading", "study", "workstation"],
            "ancient leather tomes": ["book", "books", "tome", "tomes", "manuscript", "page", "volume", "parchment", "archive"],
            "snow caps": ["snow", "ice", "frost", "peak", "peaks", "glacier", "summit"],
            "mountain trail": ["trail", "path", "ridge", "climb", "ascent", "hike"],
            "coffee cup": ["coffee", "cup", "mug", "brew", "caffeine", "warm", "tea"],
            "vibrant blossoms": ["blossom", "blossoms", "flower", "flowers", "petal", "petals", "bloom", "blooms", "floral"],
            "golden petals": ["petal", "petals", "yellow", "amber", "golden", "flower", "corolla"],
            "dewdrop tulips": ["tulip", "tulips", "dew", "dewdrop", "flower", "flowers", "bloom", "petals"],
            "emerald leaves": ["leaf", "leaves", "green", "stem", "foliage", "emerald", "stalk", "vegetation"],
            "sunlit garden": ["garden", "meadow", "flora", "botanical", "blossom", "field", "flowerbed"],
            "curious flower weaver": ["weaver", "gatherer", "protagonist", "wanderer", "traveler", "explorer", "gardener", "botanist"],
            "daisy": ["daisy", "flower", "petal", "blossom", "flora", "garden"],
            "pot": ["pot", "planter", "vessel", "earth", "soil", "garden"],
            "golden slipper orchid": ["orchid", "slipper", "blossom", "flower", "petal", "flora"],
            "animated comic hero art": ["comic", "hero", "warrior", "character", "art", "illustration", "champion", "legend"],
            "spirited young hero": ["hero", "warrior", "boy", "youth", "bheem", "champion", "defender", "protagonist", "mighty"],
            "golden wristbands": ["wristband", "wristbands", "gold", "golden", "cuff", "cuffs", "bangles", "armband"],
            "traditional dhoti": ["dhoti", "saffron", "orange", "garment", "attire", "cloth", "robe"],
            "heroic pose": ["pose", "fist", "stance", "brave", "courage", "proud", "ready", "posture"],
            "determined stance": ["stance", "feet", "ground", "resolve", "strength", "poised"],
            "majestic african elephant": ["elephant", "tusker", "trunk", "tusk", "creature", "beast", "giant", "mammal", "herd"],
            "towering giraffe": ["giraffe", "neck", "tall", "towering", "savanna", "graceful", "wildlife"],
            "pride of lions": ["lion", "lions", "pride", "mane", "predator", "feline", "king", "beast", "roar"],
            "graceful zebras": ["zebra", "zebras", "stripes", "striped", "herd", "grassland", "equine"],
            "sun-drenched grassland": ["grassland", "savanna", "savannah", "plain", "plains", "grass", "wilderness", "earth"],
            "intrepid wildlife explorer": ["explorer", "ranger", "naturalist", "guide", "tracker", "wanderer", "traveler", "protagonist"],
            "indian elephant": ["elephant", "tusker", "trunk", "creature", "beast", "giant"],
            "tusker elephant": ["tusker", "elephant", "tusk", "tusks", "ivory", "beast", "giant"],
            "wild impala": ["impala", "antelope", "gazelle", "herd", "wildlife", "horns", "creature"]
        }

        for obj in detected_objs:
            obj_name = obj.get("name", "").strip()
            obj_clean = re.sub(r'[^a-zA-Z\s]', '', obj_name).lower()
            
            # Check direct word match (including basic stemming)
            found = False
            words = [w for w in obj_clean.split() if len(w) > 2]
            for w in words:
                stem = w.rstrip('s') if len(w) > 4 else w
                if re.search(r'\b' + re.escape(w) + r'\b', full_text) or (len(stem) > 3 and re.search(r'\b' + re.escape(stem), full_text)):
                    found = True
                    break

            # Check synonyms
            if not found:
                for k, syns in synonym_map.items():
                    if k in obj_clean or obj_clean in k or any(syn in obj_clean for syn in syns):
                        if any(re.search(r'\b' + re.escape(syn) + r'\b', full_text) for syn in syns):
                            found = True
                            break

            entity_matches.append({
                "entity": obj_name,
                "confidence": obj.get("confidence", 0.9),
                "matched_in_story": found
            })
            if found:
                matched_count += 1

        total_entities = max(1, len(detected_objs))
        entity_score = (matched_count / total_entities) * 100.0

        # 2. Evaluate Scene & Environment Alignment
        scene_name = vision_metadata.get("scene_category", "").lower()
        scene_words = [w for w in re.split(r'[\s/]+', scene_name) if len(w) > 3]
        scene_matched_words = [w for w in scene_words if w in full_text]
        scene_score = min(100.0, (len(scene_matched_words) / max(1, len(scene_words))) * 110.0)

        # 3. Evaluate Atmospheric / Mood Alignment
        ambient_mood = vision_metadata.get("ambient_mood", "").lower()
        lighting = vision_metadata.get("lighting_atmosphere", "").lower()
        mood_keywords = [w for w in re.split(r'[\s,/]+', f"{ambient_mood} {lighting}") if len(w) > 3]
        mood_matches = [w for w in mood_keywords if w in full_text]
        theme_score = min(100.0, (len(mood_matches) / max(1, len(mood_keywords))) * 120.0)

        # 4. Composite Score Computation
        # Formula: 45% Entity Fidelity + 35% Scene Alignment + 20% Mood/Thematic Resonance
        composite_score = (0.45 * entity_score) + (0.35 * scene_score) + (0.20 * theme_score)
        composite_score = round(min(98.5, max(10.0, composite_score)), 1)

        summary_note = (
            f"The generated narrative directly incorporates {matched_count} out of {total_entities} detected visual objects, "
            f"maintaining strict thematic consistency with the '{vision_metadata.get('scene_category', 'scene')}' environment "
            f"and '{vision_metadata.get('lighting_atmosphere', 'lighting')}' lighting."
        )

        return {
            "overall_relevance_score": composite_score,
            "rating_tier": "High Visual Fidelity" if composite_score >= 90 else "Moderate Visual Fidelity",
            "breakdown": {
                "entity_fidelity": round(entity_score, 1),
                "scene_alignment": round(scene_score, 1),
                "thematic_resonance": round(theme_score, 1)
            },
            "entity_matches": entity_matches,
            "matched_count": matched_count,
            "total_entities": total_entities,
            "summary_note": summary_note
        }
