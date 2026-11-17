import os
import json
import random
import urllib.request
import urllib.error


# Name pools for automatic character extraction
NAMES_POOL = {
    "protagonist": ["Arjun", "Kaelen", "Maya", "Elena", "Rohan", "Lyra", "Leo", "Aria", "Dev", "Zara", "Pip", "Tara", "Nia"],
    "companion": ["Mira", "Samir", "Cassian", "Tessa", "Felix", "Nadia", "Isha", "Tobias", "Zane", "Ananya", "Raju", "Kiran"],
    "hero_protagonist": ["Bheem", "Veer", "Rudra", "Kiran"],
    "hero_companion": ["Chutki", "Raju", "Jaggu", "Kalia"]
}

PERSONALITIES = {
    "Adventure": ["Daring and inquisitive, driven by wanderlust", "Resourceful and quick-witted in the face of peril"],
    "Mystery": ["Observant, analytical, and haunted by unanswered questions", "Secretive and intuitive with an eye for subtle clues"],
    "Fantasy": ["Dreamy and attuned to ancient whispers of magic", "Fiercely loyal with an awakened mystical destiny"],
    "Sci-Fi": ["Brilliant engineer questioning the boundaries of technology", "Calculative navigator seeking truth beyond the stars"],
    "Romance": ["Tender-hearted, observant, carrying quiet yearnings", "Passionate yet guarded by past promises"],
    "Horror": ["Apprehensive yet compelled by dreadful curiosity", "Determined survivor facing the unexplainable"],
    "Comedy": ["Endearingly clumsy with an irrepressible optimistic wit", "Sarcastic realist trapped in absurd circumstances"],
    "Inspirational": ["Resilient dreamer refusing to surrender to adversity", "Kindhearted beacon of hope for their community"]
}


class StoryEngine:
    """
    Context-Aware Generative Story Engine.
    Transforms visual cues (detected objects, scene, lighting, mood)
    and user literary directives (genre, length, tone, ending) into
    a rich, diverse structured narrative: Title, Characters, Chapters, Dialogue, and Moral.
    Supports built-in multi-archetype generative engine and optional Gemini LLM API generation.
    """

    def generate_story(self, vision_metadata, genre="Adventure", length="Medium",
                       tone="Emotional", ending="Happy", custom_character=None,
                       api_key=None):
        """
        Generate structured story.
        """
        # 1. Check if external Gemini API key is provided and valid
        active_api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        if active_api_key and not active_api_key.startswith("AQ.") and active_api_key != "your_gemini_api_key_here":
            try:
                llm_story = self._generate_with_gemini(vision_metadata, genre, length, tone, ending, custom_character, active_api_key)
                if llm_story:
                    return llm_story
            except Exception as e:
                print(f"[StoryEngine] Gemini API call note: {e}. Falling back to contextual narrative engine.")

        # 2. Use Built-in Context-Aware Multi-Archetype Narrative Engine
        return self._generate_contextual_story(vision_metadata, genre, length, tone, ending, custom_character)

    def _generate_contextual_story(self, vision_metadata, genre, length, tone, ending, custom_character):
        """
        Multi-archetype contextual narrative generation engine.
        Ensures dramatic variety between consecutive generations and distinct image themes.
        """
        scene_name = vision_metadata.get("scene_category", "Coastal Shoreline / Beach")
        scene_key = vision_metadata.get("scene_key", "beach")
        lighting = vision_metadata.get("lighting_atmosphere", "Golden Sunset / Radiant Dusk")
        ambient_mood = vision_metadata.get("ambient_mood", "Tranquil, Reflective")
        raw_objects = vision_metadata.get("detected_objects", [])
        detected_objs = [o["name"] for o in raw_objects]
        caption = vision_metadata.get("generated_caption", "")

        # Lead physical object cues
        non_human_objs = [o for o in detected_objs if not any(w in o.lower() for w in ["person", "traveler", "child", "figure", "explorer", "hero", "companion", "caretaker", "weaver", "ranger"])]
        lead_obj = non_human_objs[0] if non_human_objs else (detected_objs[0] if detected_objs else "the surroundings")
        secondary_obj = non_human_objs[1] if len(non_human_objs) > 1 else (detected_objs[1] if len(detected_objs) > 1 else "the horizon")
        extra_objs = non_human_objs[2:] if len(non_human_objs) > 2 else []

        # Grammar helper for plural / singular objects
        is_plural = (lead_obj.lower().endswith("s") and not lead_obj.lower().endswith("ss")) or any(
            lead_obj.lower().endswith(w) for w in ["skyscrapers", "lights", "vehicles", "pavements", "pedestrians", "blossoms", "petals", "tulips", "leaves", "tomes", "shelves", "caps", "waters", "waves", "fields", "zebras", "lions"]
        )
        verb_is = "are" if is_plural else "is"
        verb_feel = "feel" if is_plural else "feels"
        pronoun_they = "they" if is_plural else "it"

        # Categorical scene context booleans
        is_safari = scene_key in ["safari_wildlife"] or any(any(w in o.lower() for w in ["elephant", "lion", "zebra", "giraffe", "wildlife", "safari", "savanna", "impala", "tusker"]) for o in detected_objs)
        is_city = scene_key in ["city"] or any("skyscraper" in o.lower() or "city" in o.lower() for o in detected_objs)
        is_flower = scene_key in ["flower_garden"] or any("tulip" in o.lower() or "blossom" in o.lower() or "petal" in o.lower() or "daisy" in o.lower() for o in detected_objs)
        is_mountain = scene_key in ["mountain"] or any("mountain" in o.lower() or "peak" in o.lower() for o in detected_objs)
        is_beach = scene_key in ["beach"] or any("ocean" in o.lower() or "sea" in o.lower() or "boat" in o.lower() for o in detected_objs)
        is_hero_scene = scene_key == "animated_character" or any("hero" in o.lower() or "comic" in o.lower() for o in detected_objs)

        # 1. Determine Characters based on Scene & Directives
        if custom_character and custom_character.get("name"):
            p_name = custom_character.get("name")
        elif is_hero_scene:
            p_name = random.choice(NAMES_POOL["hero_protagonist"])
        else:
            p_name = random.choice(NAMES_POOL["protagonist"])

        p_personality = random.choice(PERSONALITIES.get(genre, PERSONALITIES["Adventure"]))

        if is_hero_scene:
            c_name = random.choice([n for n in NAMES_POOL["hero_companion"] if n != p_name])
            c_role = "Loyal Comrade in Arms"
            c_personality = "Spirited, brave companion always ready for action"
        elif is_safari:
            c_name = random.choice([n for n in NAMES_POOL["companion"] if n != p_name])
            c_role = "Field Tracker & Naturalist"
            c_personality = "Patient wildlife observer with deep respect for animal habitats"
        else:
            c_name = random.choice([n for n in NAMES_POOL["companion"] if n != p_name])
            c_role = "Companion & Confidant"
            c_personality = "Attentive and insightful friend with unwavering loyalty"

        characters = [
            {
                "name": p_name,
                "role": "Protagonist",
                "personality": p_personality,
                "visual_connection": f"Inspired by the central presence amidst the {scene_name.lower()}."
            },
            {
                "name": c_name,
                "role": c_role,
                "personality": c_personality,
                "visual_connection": f"Shares the journey and exploration near {lead_obj.lower()}."
            }
        ]

        # 2. Select Narrative Archetype
        if is_hero_scene:
            archetype_pool = ["heroic_trial", "heroic_trial", "comedic_escapade"]
        elif is_safari:
            archetype_pool = ["wonder_discovery", "heroic_trial", "sanctuary_harmony"]
        elif is_city:
            archetype_pool = ["urban_expedition", "whispering_enigma", "heroic_trial"]
        elif is_flower:
            archetype_pool = ["wonder_discovery", "sanctuary_harmony", "whispering_enigma"]
        elif genre in ["Mystery", "Horror"]:
            archetype_pool = ["whispering_enigma"]
        elif genre in ["Comedy"]:
            archetype_pool = ["comedic_escapade", "heroic_trial"]
        elif genre in ["Romance", "Inspirational"]:
            archetype_pool = ["sanctuary_harmony", "wonder_discovery"]
        else:
            archetype_pool = ["wonder_discovery", "heroic_trial", "whispering_enigma", "sanctuary_harmony"]

        archetype = random.choice(archetype_pool)

        # 3. Dynamic Title Synthesis
        clean_lead = lead_obj.split('/')[0].strip()
        clean_scene = scene_name.split('/')[0].strip()

        if is_safari:
            title_pool = [
                f"Guardians of the {clean_lead}",
                f"Echoes Across the Golden Savanna",
                f"The Great Migration of {clean_lead}",
                f"Sunset Over the Untamed Wild"
            ]
        elif is_city:
            title_pool = [
                f"The Beacon of the {clean_lead}",
                f"Skyline of a Thousand Dreams",
                f"Whispers Above {clean_scene}",
                f"The Midnight Pulse of the Metropolis"
            ]
        elif is_hero_scene:
            title_pool = [
                f"The Mighty Feat of {p_name}",
                f"Defense of the Golden Valley",
                f"The Trial of the {clean_lead}",
                f"Valor Across the Realm"
            ]
        else:
            title_pool = [
                f"The Secret of the {clean_lead}",
                f"The Whispering Tapestry of {clean_scene}",
                f"Awakening of the {clean_lead}",
                f"Where the {clean_lead} Blossoms"
            ]
        title = random.choice(title_pool)

        # 4. Dynamic Chapters Construction
        multiplier = 1 if length == "Short" else (2 if length == "Medium" else 3)
        extra_obj_phrase = f", alongside glimpses of {extra_objs[0].lower()}" if extra_objs else ""

        if is_safari:
            ch1_head = "Chapter 1: Dawn Across the Savanna"
            ch2_head = "Chapter 2: Call of the Wild Herd"
            ch3_head = "Chapter 3: The Sacred Gathering"
            ch4_head = "Chapter 4: Guardians of the Horizon"

            intro_text = (
                f"A profound silence descended upon the {scene_name.lower()} as the first golden rays broke across the sweeping plains. "
                f"Under the breathtaking warmth of {lighting.lower()}, {p_name} paused, spellbound by the sheer majesty of the wilderness. "
                f"Moving gracefully across the horizon, {lead_obj.lower()} appeared like living royalty against the vast expanse, radiating {ambient_mood.lower()}."
            )
            if multiplier >= 2:
                intro_text += (
                    f" Beside {p_name}, {c_name} raised a pair of brass field binoculars, whispering in awe at the sheer scale of the landscape. "
                    f"The morning breeze carried the scent of sun-warmed grass and distant watering holes, a timeless rhythm untouched by modernity."
                )
            if multiplier >= 3:
                intro_text += f" In the distance, {secondary_obj.lower()}{extra_obj_phrase} completed a living panorama of wild harmony."

            conflict_text = (
                f"As {p_name} and {c_name} watched from a respectful vantage point, the herd paused near {secondary_obj.lower()}. "
                f"A seasonal shift in the river currents had obscured the traditional crossing path, causing the younger animals to hesitate. "
                f"'{p_name}, look,' {c_name} murmured softly. 'They are calculating the safest path across the open terrain.'"
            )
            if multiplier >= 2:
                conflict_text += (
                    f" The tension on the plains was palpable, yet peaceful. "
                    f"Every creature seemed connected by an instinctual trust that had guided their ancestors across these grasslands for millennia."
                )
            if multiplier >= 3:
                conflict_text += f" Rather than interfering, the travelers understood their role was simply to observe and protect the sanctuary from afar."

            climax_text = (
                f"With a confident, rumbling call that vibrated through the earth, the leader of {lead_obj.lower()} took the first decisive stride forward. "
                f"The golden light of {lighting.lower()} illuminated dust clouds swirling like powdered amber around their giant footsteps. "
                f"In an awe-inspiring procession of strength and grace, the entire gathering navigated the crossing smoothly, reaching fertile grazing pastures."
            )
            if multiplier >= 2:
                climax_text += (
                    f" {p_name} and {c_name} smiled in pure relief and wonder as {secondary_obj.lower()} basked in the triumphant evening glow. "
                    f"Witnessing such raw natural resilience left an indelible mark upon their spirits."
                )
            if multiplier >= 3:
                climax_text += f" It was a masterclass in nature's quiet power—proof that untamed life moves to an enduring, magnificent design."

        elif is_city:
            ch1_head = "Chapter 1: The Golden Skyline"
            ch2_head = "Chapter 2: Canyons of Glass and Steel"
            ch3_head = "Chapter 3: Illumination of the Heights"
            ch4_head = "Chapter 4: Pulse of a Thousand Dreams"

            intro_text = (
                f"The evening arrived with electrifying brilliance across the {scene_name.lower()}. "
                f"Under the radiant canopy of {lighting.lower()}, {p_name} gazed upward at the towering silhouettes that defined the modern world. "
                f"Soaring proudly into the amber sky, {lead_obj.lower()} caught the fading sunlight, shimmering like architectural monuments bathed in {ambient_mood.lower()}."
            )
            if multiplier >= 2:
                intro_text += (
                    f" Beside {p_name}, {c_name} consulted the metropolitan transit map, looking out over the bustling avenues below. "
                    f"The city hummed with millions of intertwined stories, an urban symphony powered by ambition and boundless human ingenuity."
                )
            if multiplier >= 3:
                intro_text += f" Along the grand concourse, {secondary_obj.lower()}{extra_obj_phrase} pulsed with the vibrant energy of metropolitan life."

            conflict_text = (
                f"Navigating the observation promenade near {lead_obj.lower()}, {p_name} noticed a rare historical blueprint etched into the central plaza wall. "
                f"It revealed an architectural secret: the towers had been deliberately engineered to align with the equinox sunset. "
                f"'Look closely at the geometry,' {c_name} said, pointing toward {secondary_obj.lower()}. 'In just a few moments, the reflection will converge.'"
            )
            if multiplier >= 2:
                conflict_text += (
                    f" Crowds of commuters began pausing in their tracks, looking up from screens and busy schedules. "
                    f"A shared anticipation swept through the urban plaza as the sun descended toward the glass horizon."
                )
            if multiplier >= 3:
                conflict_text += f" For a brief interval, the relentless rush of city life paused in collective wonder."

            climax_text = (
                f"Right as the sun touched the horizon, a breathtaking beam of golden fire refracted through {lead_obj.lower()}. "
                f"A brilliant cascade of warm amber light washed across every boulevard, rooftop, and avenue, turning the steel jungle into a palace of gold. "
                f"The entire skyline erupted into radiant brilliance, perfectly harmonizing human innovation with natural splendor."
            )
            if multiplier >= 2:
                climax_text += (
                    f" Cheers and gasps echoed from the observation terrace as {secondary_obj.lower()} sparkled under the sunset glow. "
                    f"{p_name} turned to {c_name} with an inspired smile, reminded that even in the heart of concrete and steel, wonder thrives."
                )
            if multiplier >= 3:
                climax_text += f" It was a breathtaking tribute to human creativity, forever linking the city to the eternal rhythm of the sun."

        elif is_hero_scene or archetype == "heroic_trial":
            ch1_head = "Chapter 1: The Clarion Call"
            ch2_head = "Chapter 2: The Colossal Obstacle"
            ch3_head = "Chapter 3: Surge of the Pure Heart"
            ch4_head = "Chapter 4: Triumph in the Sun"

            intro_text = (
                f"The day began with explosive vigor across the {scene_name.lower()}. "
                f"Under the vibrant canopy of {lighting.lower()}, {p_name} stood tall, radiating boundless confidence and strength. "
                f"Nearby, {c_name} signaled urgently, pointing toward {lead_obj.lower()} where a sudden disruption called for action. "
                f"Every fiber of the surroundings pulsed with an aura of {ambient_mood.lower()}."
            )
            if multiplier >= 2:
                intro_text += (
                    f" For {p_name}, challenges were not obstacles to be feared, but invitations to protect those who could not stand alone. "
                    f"Tightening their grip and steadying their posture near {secondary_obj.lower()}, the hero prepared for action."
                )
            if multiplier >= 3:
                intro_text += f" The onlookers watched from afar, confident that with {p_name} on watch, no peril would overcome their land."

            conflict_text = (
                f"Upon reaching the perimeter of {lead_obj.lower()}, the magnitude of the trial became unmistakably clear. "
                f"A massive landslide had severed the vital pathway, wedging itself tightly against {secondary_obj.lower()}{extra_obj_phrase}. "
                f"'{p_name}, ordinary strength won't budge this!' {c_name} cried out, scanning the precarious precipice."
            )
            if multiplier >= 2:
                conflict_text += (
                    f" A chorus of worried whispers rose from the gathered spectators. "
                    f"Yet beneath {p_name}'s brow, there was neither panic nor hesitation—only the steadfast resolve that defines a true champion."
                )
            if multiplier >= 3:
                conflict_text += f" Drawing deep courage from within, {p_name} planted both feet firmly into the earth and locked into a resolute stance."

            climax_text = (
                f"With a resounding battle cry, {p_name} lunged forward, placing both hands against the crushing weight. "
                f"Veins surged with legendary vigor as the ground trembled beneath their stance. "
                f"In a breathtaking display of raw courage and determination, the colossal barrier shifted, groaned, and tumbled harmlessly away from {secondary_obj.lower()}!"
            )
            if multiplier >= 2:
                climax_text += (
                    f" The air filled with thunderous applause as {c_name} leapt in celebration. "
                    f"The light of {lighting.lower()} broke triumphantly over the cleared path, shining down like a mantle of gold."
                )
            if multiplier >= 3:
                climax_text += f" It was a masterclass in heroism—proof that strength guided by kindness can conquer the most impossible obstacles."

        elif is_flower or archetype == "wonder_discovery":
            ch1_head = "Chapter 1: The Luminous Threshold"
            ch2_head = "Chapter 2: The Whispering Petals"
            ch3_head = "Chapter 3: The Secret Convergence"
            ch4_head = "Chapter 4: A Tapestry Reborn"

            intro_text = (
                f"A breathtaking hush descended upon the {scene_name.lower()} as the first rays broke through the horizon. "
                f"Surrounded by {lighting.lower()}, {p_name} walked slowly along the trail, spellbound by the sheer vitality of the earth. "
                f"Prominently before them stood {lead_obj.lower()}, catching the morning brilliance like a living jewel amidst {ambient_mood.lower()}."
            )
            if multiplier >= 2:
                intro_text += (
                    f" Guided by an instinct older than memory, {c_name} followed close behind, carrying a satchel of woven twine and glass vials. "
                    f"The atmosphere felt charged with an electric stillness, as if the landscape had awaited this exact visitor for centuries."
                )
            if multiplier >= 3:
                intro_text += f" Every brush of wind against {secondary_obj.lower()}{extra_obj_phrase} released an intoxicating blend of fresh nectar and sun-warmed earth."

            conflict_text = (
                f"As {p_name} knelt beside {lead_obj.lower()}, an extraordinary pattern emerged across the radiant surface. "
                f"{c_name} leaned in, eyes wide with astonishment: 'Look at the subtle glow... it's pulsing with pure natural energy!' "
                f"What had begun as a leisurely walk through {scene_name.lower()} was unfolding into an encounter with the heart of nature itself."
            )
            if multiplier >= 2:
                conflict_text += (
                    f" Yet with this revelation came an urgent realization: the delicate harmony was fragile, vulnerable to the shifting elements. "
                    f"They had only until the midday heat arrived to understand the message embedded within the landscape."
                )
            if multiplier >= 3:
                conflict_text += f" Carefully tracing the contours near {secondary_obj.lower()}, {p_name} unlocked the subtle alignment connecting each element."

            climax_text = (
                f"With reverent focus, {p_name} channeled the natural resonance, harmonizing the surrounding elements. "
                f"In an instant of pure wonder, {lead_obj.lower()} shimmered in a cascade of iridescent color, mirroring the majesty of {lighting.lower()}. "
                f"A wave of fragrant, soothing warmth washed across the entire expanse, restoring vibrant life to every dormant root."
            )
            if multiplier >= 2:
                climax_text += (
                    f" Both {p_name} and {c_name} stood speechless as {secondary_obj.lower()} glowed in sympathetic unison. "
                    f"They were no longer mere spectators of beauty; they had become guardians of its living legacy."
                )
            if multiplier >= 3:
                climax_text += f" Nature had revealed its most tender secret, rewarding their gentleness with an unforgettable spectacle of light."

        else: # sanctuary_harmony / default
            ch1_head = "Chapter 1: The Amber Sanctuary"
            ch2_head = "Chapter 2: Footsteps in the Stillness"
            ch3_head = "Chapter 3: The Shared Revelation"
            ch4_head = "Chapter 4: An Everlasting Peace"

            intro_text = (
                f"A sublime peace enveloped the {scene_name.lower()}, soothing the heart of all who walked its paths. "
                f"Under the gentle embrace of {lighting.lower()}, {p_name} found the sanctuary they had sought for so long. "
                f"The peaceful silhouette of {lead_obj.lower()} rested in effortless cadence with {ambient_mood.lower()}."
            )
            if multiplier >= 2:
                intro_text += (
                    f" Walking side by side with {c_name}, words were unnecessary; the shared silence spoke volumes. "
                    f"Here, far from the hurried clamor of daily strife, time flowed like honey through the landscape."
                )
            if multiplier >= 3:
                intro_text += f" Every glance toward {secondary_obj.lower()}{extra_obj_phrase} felt like a gentle reminder of life's quiet abundance."

            conflict_text = (
                f"Pausing beside {lead_obj.lower()}, {p_name} reflected on the challenges that had brought them here. "
                f"A quiet dilemma weighed on their mind: could the peace discovered in the {scene_name.lower()} endure once they returned to the world outside? "
                f"{c_name} reached over gently: 'The sanctuary isn't just the ground we stand on; it's what we choose to nurture within us.'"
            )
            if multiplier >= 2:
                conflict_text += (
                    f" The simplicity of the truth settled over them like the evening warmth. "
                    f"To protect this harmony, they realized they must share its healing beauty with others."
                )
            if multiplier >= 3:
                conflict_text += f" Looking around at {secondary_obj.lower()}, they knew their purpose had become clear."

            climax_text = (
                f"In a moment of profound gratitude, {p_name} took a deep, revitalizing breath near {lead_obj.lower()}, releasing all remaining fatigue and doubt. "
                f"The landscape seemed to lean forward, basking in the shared warmth under the radiant sky of {lighting.lower()}. "
                f"A deep, revitalizing clarity washed over the soul, renewing their strength and purpose."
            )
            if multiplier >= 2:
                climax_text += (
                    f" {c_name} smiled warmly, seeing the light return to {p_name}'s eyes. "
                    f"Together, they recognized that true healing is a quiet, living sanctuary."
                )
            if multiplier >= 3:
                climax_text += f" The setting sun sealed this realization into an enduring memory that would guide them forever."

        # Resolution based on user-chosen ending
        if ending == "Happy" or ending == "Triumphant":
            resolution_text = (
                f"As night gently welcomed the stars over the {scene_name.lower()}, an unbroken sense of fulfillment reigned. "
                f"{p_name} turned to {c_name} with an unshakeable smile. "
                f"They had honored the spirit of {lead_obj.lower()} and protected the harmony of their world. "
                f"Ahead lay new dawns, but this day would be remembered forever as a triumph of heart and spirit."
            )
        elif ending == "Unexpected":
            resolution_text = (
                f"Just as the final shadows settled over {lead_obj.lower()}, an unexpected golden shimmer rose into the twilight air. "
                f"{p_name} and {c_name} exchanged a startled, thrilled glance. "
                f"Their adventure had not concluded at all; it had merely opened the doorway to a much greater realm of wonder."
            )
        elif ending == "Bittersweet":
            resolution_text = (
                f"The warmth of {lighting.lower()} gradually surrendered to the cool night breeze. "
                f"Though the journey was fulfilled and peace restored near {lead_obj.lower()}, {p_name} knew that some chapters in life must close to allow new beginnings. "
                f"Carrying fond memories and lessons etched in memory, they began the journey homeward beneath the quiet stars."
            )
        else: # Open-ended
            resolution_text = (
                f"The horizon stretched endlessly beyond the {scene_name.lower()}, blurring into shades of violet and silver. "
                f"Neither {p_name} nor {c_name} felt the need to speak, for some questions are more beautiful left open. "
                f"With hearts full of anticipation, they watched the twilight unfold, ready for whatever tomorrow might bring."
            )

        chapters = [
            {"number": 1, "heading": ch1_head, "content": intro_text},
            {"number": 2, "heading": ch2_head, "content": conflict_text},
            {"number": 3, "heading": ch3_head, "content": climax_text},
            {"number": 4, "heading": ch4_head, "content": resolution_text}
        ]

        # 5. Dynamic Dialogue generation tailored to scene & grammar
        if is_safari:
            dialogues = [
                {"speaker": p_name, "line": f"Have you ever seen anything so awe-inspiring? The {lead_obj.lower()} {verb_feel} like royalty of the open plains."},
                {"speaker": c_name, "line": f"It's breathtaking, {p_name}. The entire {scene_name.lower()} is alive with untamed beauty."},
                {"speaker": p_name, "line": f"Let's make sure we preserve this wilderness so future generations can witness its majesty."}
            ]
        elif is_city:
            dialogues = [
                {"speaker": p_name, "line": f"Look at the way the sunset reflects off {lead_obj.lower()}... it's pure architectural poetry."},
                {"speaker": c_name, "line": f"The entire {scene_name.lower()} seems to glow when the evening arrives."},
                {"speaker": p_name, "line": f"Even in the busiest streets, there's always a quiet moment of wonder if you look up."}
            ]
        elif is_hero_scene:
            dialogues = [
                {"speaker": p_name, "line": f"Stand back, {c_name}! As long as I'm here, nothing can harm our home!"},
                {"speaker": c_name, "line": f"I've got your back, {p_name}! Together, no obstacle can stop us!"},
                {"speaker": p_name, "line": f"Courage and heart—that's all we need to clear the way!"}
            ]
        else:
            dialogues = [
                {"speaker": p_name, "line": f"Have you ever seen anything so vibrant? The {lead_obj.lower()} {verb_feel} alive with light."},
                {"speaker": c_name, "line": f"It's breathtaking, {p_name}. The entire {scene_name.lower()} is singing in harmony."},
                {"speaker": p_name, "line": f"Let's carry this warmth with us as we journey forward."}
            ]

        # 6. Dynamic Moral / Thematic Takeaway
        morals = {
            "Adventure": "True discovery consists not in seeking new landscapes, but in having new eyes to witness the wonder before us.",
            "Mystery": "The most profound truths are rarely shouted; they whisper quietly to those patient enough to listen.",
            "Fantasy": "Magic does not dwell in the impossible, but in the reverence with which we greet each passing sunset.",
            "Sci-Fi": "No matter how vast the cosmos or how deep our machines, the human spirit remains the ultimate explorer.",
            "Romance": "Moments of beauty are multiplied when shared with someone who sees the world through the same gentle light.",
            "Horror": "Courage is not the absence of dread, but the quiet resolve to press on even when shadows lengthen.",
            "Comedy": "Life's most breathtaking epics often begin with a stumble, a laugh, and a leap into the unexpected.",
            "Inspirational": "Every sunset carries the promise of a dawn, reminding us that even the longest journey begins with a single faithful step."
        }
        moral = morals.get(genre, morals["Inspirational"])

        return {
            "title": title,
            "genre": genre,
            "length": length,
            "tone": tone,
            "ending": ending,
            "scene_setting": scene_name,
            "image_caption": caption,
            "characters": characters,
            "chapters": chapters,
            "dialogue": dialogues,
            "moral": moral
        }

    def _generate_with_gemini(self, vision_metadata, genre, length, tone, ending, custom_character, api_key):
        """Call Gemini API with structured JSON schema prompt."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
You are an award-winning author. Analyze the following visual image metadata and craft an original, deeply evocative, structured story.

VISUAL METADATA EXTRACTED FROM IMAGE:
- Scene Environment: {vision_metadata.get('scene_category')}
- Detected Objects: {', '.join([o['name'] for o in vision_metadata.get('detected_objects', [])])}
- Lighting & Atmosphere: {vision_metadata.get('lighting_atmosphere')}
- Ambient Mood: {vision_metadata.get('ambient_mood')}
- Visual Caption: {vision_metadata.get('generated_caption')}

USER DIRECTIVES:
- Genre: {genre}
- Length: {length} (Short: ~250 words, Medium: ~500 words, Long: ~800 words)
- Tone: {tone}
- Ending: {ending}
{f'- Custom Character: {custom_character}' if custom_character else ''}

OUTPUT STRICTLY VALID JSON MATCHING THIS EXACT SCHEMA:
{{
  "title": "Evocative Title",
  "genre": "{genre}",
  "length": "{length}",
  "tone": "{tone}",
  "ending": "{ending}",
  "scene_setting": "{vision_metadata.get('scene_category')}",
  "image_caption": "{vision_metadata.get('generated_caption')}",
  "characters": [
    {{"name": "Name", "role": "Role", "personality": "Personality description", "visual_connection": "How they connect to image"}}
  ],
  "chapters": [
    {{"number": 1, "heading": "Chapter 1: ...", "content": "Text..."}},
    {{"number": 2, "heading": "Chapter 2: ...", "content": "Text..."}},
    {{"number": 3, "heading": "Chapter 3: ...", "content": "Text..."}},
    {{"number": 4, "heading": "Chapter 4: ...", "content": "Text..."}}
  ],
  "dialogue": [
    {{"speaker": "Name", "line": "Spoken line..."}}
  ],
  "moral": "Philosophical takeaway or moral"
}}
Do not include markdown ticks, output only raw JSON.
"""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.75,
                "response_mime_type": "application/json"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            # Strip any accidental markdown formatting
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return json.loads(raw_text.strip())
