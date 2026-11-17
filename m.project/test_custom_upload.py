import os
import sys
import json
import urllib.request
import mimetypes
from PIL import Image, ImageDraw

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:5000"

def create_user_custom_image():
    """Create a simulated user photo: e.g. a pet dog in a grassy meadow"""
    img = Image.new("RGB", (640, 480), (85, 170, 85)) # green meadow
    draw = ImageDraw.Draw(img)
    
    # Sky
    draw.rectangle([0, 0, 640, 200], fill=(135, 206, 235))
    # Sun
    draw.ellipse([500, 40, 580, 120], fill=(255, 240, 100))
    # Hills
    draw.arc([100, 120, 600, 360], 180, 360, fill=(60, 140, 60), width=6)
    
    # Dog silhouette / shape
    # Body
    draw.ellipse([260, 260, 380, 340], fill=(180, 120, 60))
    # Head
    draw.ellipse([350, 220, 410, 280], fill=(180, 120, 60))
    # Snout
    draw.ellipse([390, 250, 430, 275], fill=(160, 100, 50))
    draw.ellipse([420, 255, 428, 263], fill=(20, 20, 20)) # nose
    # Ears
    draw.polygon([(365, 225), (350, 260), (375, 250)], fill=(140, 90, 40))
    # Legs
    draw.rectangle([280, 330, 298, 400], fill=(160, 100, 50))
    draw.rectangle([340, 330, 358, 400], fill=(160, 100, 50))
    # Tail
    draw.arc([220, 240, 280, 300], 90, 270, fill=(180, 120, 60), width=8)

    save_path = os.path.join(os.path.dirname(__file__), "my_custom_dog_photo.jpg")
    img.save(save_path, quality=95)
    print(f"Created custom user test photo: {save_path}")
    return save_path

def post_multipart_form(url, file_field, file_path):
    boundary = "----VisionStoryBoundaryXYZ12345"
    filename = os.path.basename(file_path)
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body))
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_custom_user_image_upload():
    print("\n--- Testing Custom User Image Upload ---")
    custom_img_path = create_user_custom_image()

    # 1. Upload custom image via multipart/form-data
    res = post_multipart_form(f"{BASE_URL}/api/upload", "image", custom_img_path)
    assert res["success"] is True, f"Upload failed: {res}"
    print(f"[OK] Custom image uploaded successfully! Image ID: {res['image_id']}")
    print(f"     Detected Scene: {res['vision_metadata']['scene_category']}")
    print(f"     Detected Objects: {[o['name'] for o in res['vision_metadata']['detected_objects']]}")
    print(f"     Laplacian Sharpness: {res['diagnostics']['sharpness']['laplacian_variance']}")
    print(f"     Tensor Shape: {res['diagnostics']['pytorch_tensor']['shape']}")

    # 2. Generate Story for this custom image
    gen_payload = {
        "image_id": res["image_id"],
        "genre": "Adventure",
        "length": "Medium",
        "tone": "Emotional",
        "ending": "Happy",
        "custom_character": {"name": "Buddy"}
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/generate-story",
        data=json.dumps(gen_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        story_res = json.loads(resp.read().decode("utf-8"))
        assert story_res["success"] is True
        print(f"[OK] Story for custom image generated successfully!")
        print(f"     Title: '{story_res['story']['title']}'")
        print(f"     Protagonist: '{story_res['story']['characters'][0]['name']}'")
        print(f"     Relevance Score: {story_res['relevance']['overall_relevance_score']}%")
        print(f"     Moral: \"{story_res['story']['moral']}\"")

if __name__ == "__main__":
    test_custom_user_image_upload()
