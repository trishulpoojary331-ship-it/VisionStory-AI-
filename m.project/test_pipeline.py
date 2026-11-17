import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_pipeline():
    print("==================================================")
    print("Starting VisionStory AI Pipeline Automated Tests")
    print("==================================================")

    # 1. Imports Verification
    print("\n[Step 1] Verifying Core Imports...")
    import torch
    import torchvision
    import reportlab
    import cv2
    import PIL
    import flask
    print(f"  [OK] PyTorch version: {torch.__version__}")
    print(f"  [OK] Torchvision version: {torchvision.__version__}")
    print(f"  [OK] ReportLab version: {reportlab.__version__}")
    print(f"  [OK] OpenCV version: {cv2.__version__}")

    # 2. Image Preprocessing Test
    print("\n[Step 2] Testing PyTorch Preprocessing Pipeline...")
    from ml.preprocessor import ImagePreprocessor
    preprocessor = ImagePreprocessor()
    test_image_path = os.path.join(os.path.dirname(__file__), "static", "samples", "beach_sunset.jpg")
    assert os.path.exists(test_image_path), f"Test sample not found: {test_image_path}"

    tensor, diagnostics, pil_img = preprocessor.preprocess(test_image_path)
    assert tensor is not None, "Tensor should not be None"
    assert tensor.shape == (1, 3, 224, 224), f"Expected tensor shape (1, 3, 224, 224), got {tensor.shape}"
    print(f"  [OK] Preprocessed Tensor Shape: {tensor.shape}")
    print(f"  [OK] Laplacian Sharpness Variance: {diagnostics['sharpness']['laplacian_variance']}")
    print(f"  [OK] Lighting Category: {diagnostics['lighting']['category']}")
    print(f"  [OK] Dominant Palette Colors: {len(diagnostics['dominant_colors'])}")

    # 3. Vision Model & Understanding Test
    print("\n[Step 3] Testing Vision Model & Understanding...")
    from ml.vision_model import VisionModel
    vision_engine = VisionModel()
    vision_meta = vision_engine.analyze_image(tensor, diagnostics, pil_img, filename="beach_sunset.jpg")
    print(f"  [OK] Scene Category: {vision_meta['scene_category']}")
    print(f"  [OK] Detected Objects: {[o['name'] for o in vision_meta['detected_objects']]}")
    print(f"  [OK] Lighting & Atmosphere: {vision_meta['lighting_atmosphere']}")
    print(f"  [OK] Generated Caption: {vision_meta['generated_caption']}")
    assert len(vision_meta['detected_objects']) > 0, "Should detect at least 1 object"

    # 4. Context-Aware Story Generation Engine Test
    print("\n[Step 4] Testing Story Generation Engine...")
    from generators.story_engine import StoryEngine
    story_engine = StoryEngine()
    story = story_engine.generate_story(
        vision_metadata=vision_meta,
        genre="Adventure",
        length="Medium",
        tone="Emotional",
        ending="Happy"
    )
    print(f"  [OK] Generated Title: {story['title']}")
    print(f"  [OK] Character 1: {story['characters'][0]['name']} ({story['characters'][0]['role']})")
    print(f"  [OK] Chapters Count: {len(story['chapters'])}")
    print(f"  [OK] Dialogues Count: {len(story['dialogue'])}")
    print(f"  [OK] Moral: {story['moral']}")
    assert len(story['chapters']) == 4, "Should have 4 acts/chapters"

    # 5. Story Relevance Scorer Test
    print("\n[Step 5] Testing Story Relevance Evaluation Scorer...")
    from ml.relevance_scorer import StoryRelevanceScorer
    relevance_scorer = StoryRelevanceScorer()
    relevance = relevance_scorer.evaluate(vision_meta, story)
    print(f"  [OK] Overall Relevance Score: {relevance['overall_relevance_score']}%")
    print(f"  [OK] Fidelity Tier: {relevance['rating_tier']}")
    print(f"  [OK] Entity Fidelity: {relevance['breakdown']['entity_fidelity']}%")
    print(f"  [OK] Scene Alignment: {relevance['breakdown']['scene_alignment']}%")
    print(f"  [OK] Thematic Resonance: {relevance['breakdown']['thematic_resonance']}%")
    assert relevance['overall_relevance_score'] >= 80, "Expected relevance score >= 80%"

    # 6. PDF Storybook Generation Test
    print("\n[Step 6] Testing PDF Storybook Generator...")
    from generators.pdf_generator import PDFStorybookGenerator
    pdf_gen = PDFStorybookGenerator()
    test_pdf_path = os.path.join(os.path.dirname(__file__), "test_storybook.pdf")
    pdf_gen.generate_pdf(story, test_image_path, relevance, output_path=test_pdf_path)
    assert os.path.exists(test_pdf_path), "PDF file should be created"
    pdf_size = os.path.getsize(test_pdf_path)
    print(f"  [OK] PDF Storybook generated successfully! File size: {pdf_size} bytes ({round(pdf_size/1024, 1)} KB)")

    print("\n==================================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()
