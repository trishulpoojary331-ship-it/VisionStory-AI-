import urllib.request
import json
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"

def test_endpoints():
    print("==================================================")
    print("Testing VisionStory AI Live HTTP Endpoints")
    print("==================================================")

    # 1. Test GET /
    print("\n[Test 1] Testing GET / (Static Web UI)...")
    req = urllib.request.Request(f"{BASE_URL}/")
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        html = res.read().decode("utf-8")
        assert "VisionStory" in html
        print("  [OK] Index HTML served successfully (Status 200, length:", len(html), "chars)")

    # 2. Test GET /api/samples
    print("\n[Test 2] Testing GET /api/samples...")
    req = urllib.request.Request(f"{BASE_URL}/api/samples")
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["success"] is True
        assert len(data["samples"]) == 6
        print(f"  [OK] Returned {len(data['samples'])} preset benchmark samples:")
        for s in data["samples"]:
            print(f"       - {s['title']} ({s['filename']})")

    # 3. Test POST /api/upload (sample_id='beach_sunset')
    print("\n[Test 3] Testing POST /api/upload with preset 'beach_sunset'...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/upload",
        data=json.dumps({"sample_id": "beach_sunset"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        upload_data = json.loads(res.read().decode("utf-8"))
        assert upload_data["success"] is True
        image_id = upload_data["image_id"]
        print(f"  [OK] Image uploaded successfully! Image ID: {image_id}")
        print(f"       - Preprocessed Tensor: {upload_data['diagnostics']['pytorch_tensor']['shape']}")
        print(f"       - Laplacian Sharpness: {upload_data['diagnostics']['sharpness']['laplacian_variance']}")
        print(f"       - Detected Scene: {upload_data['vision_metadata']['scene_category']}")
        print(f"       - Visual Caption: {upload_data['vision_metadata']['generated_caption']}")

    # 4. Test POST /api/generate-story
    print("\n[Test 4] Testing POST /api/generate-story...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/generate-story",
        data=json.dumps({
            "image_id": image_id,
            "genre": "Adventure",
            "length": "Medium",
            "tone": "Emotional",
            "ending": "Happy",
            "custom_character": {"name": "Arjun"}
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        story_res = json.loads(res.read().decode("utf-8"))
        assert story_res["success"] is True
        story_id = story_res["story_id"]
        story = story_res["story"]
        relevance = story_res["relevance"]
        print(f"  [OK] Story generated successfully! Story ID: {story_id}")
        print(f"       - Title: {story['title']}")
        print(f"       - Protagonist: {story['characters'][0]['name']}")
        print(f"       - Chapters: {len(story['chapters'])} acts")
        print(f"       - Dialogues: {len(story['dialogue'])} lines")
        print(f"       - Relevance Score: {relevance['overall_relevance_score']}% ({relevance['rating_tier']})")

    # 5. Test POST /api/multi-versions
    print("\n[Test 5] Testing POST /api/multi-versions (Arena)...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/multi-versions",
        data=json.dumps({
            "image_id": image_id,
            "genres": ["Adventure", "Mystery", "Inspirational"],
            "length": "Short"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        arena_res = json.loads(res.read().decode("utf-8"))
        assert arena_res["success"] is True
        print(f"  [OK] Arena generated {len(arena_res['versions'])} distinct genre takes:")
        for v in arena_res["versions"]:
            print(f"       - [{v['genre']}] '{v['story']['title']}' (Relevance: {v['relevance']['overall_relevance_score']}%)")

    # 6. Test POST /api/regenerate-story
    print("\n[Test 6] Testing POST /api/regenerate-story...")
    req = urllib.request.Request(
        f"{BASE_URL}/api/regenerate-story",
        data=json.dumps({
            "story_id": story_id,
            "genre": "Mystery",
            "tone": "Suspenseful",
            "ending": "Unexpected",
            "custom_character": {"name": "Maya"}
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        regen_res = json.loads(res.read().decode("utf-8"))
        assert regen_res["success"] is True
        print(f"  [OK] Story regenerated: '{regen_res['story']['title']}' with protagonist '{regen_res['story']['characters'][0]['name']}'")

    # 7. Test GET /api/stories (Library)
    print("\n[Test 7] Testing GET /api/stories (Library listing)...")
    req = urllib.request.Request(f"{BASE_URL}/api/stories")
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        lib_data = json.loads(res.read().decode("utf-8"))
        assert lib_data["success"] is True
        print(f"  [OK] Retrieved {len(lib_data['stories'])} saved stories from database")

    # 8. Test GET /api/export-pdf/<id>
    print("\n[Test 8] Testing GET /api/export-pdf/{story_id}...")
    req = urllib.request.Request(f"{BASE_URL}/api/export-pdf/{story_id}")
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        pdf_content = res.read()
        assert pdf_content.startswith(b"%PDF"), "Response should be valid PDF binary"
        print(f"  [OK] Exported PDF Storybook successfully! Size: {len(pdf_content)} bytes")

    print("\n==================================================")
    print("ALL SERVER ENDPOINTS VALIDATED AND WORKING 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_endpoints()
