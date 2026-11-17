import os
import io
import json
import uuid
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

from models import db, User, ImageUpload, Story, StoryVersion
from ml.preprocessor import ImagePreprocessor
from ml.vision_model import VisionModel
from ml.relevance_scorer import StoryRelevanceScorer
from generators.story_engine import StoryEngine
from generators.pdf_generator import PDFStorybookGenerator, REPORTLAB_AVAILABLE

# App configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'visionstory-ai-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visionstory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 # 20 MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions & engines
db.init_app(app)

preprocessor = ImagePreprocessor()
vision_engine = VisionModel()
relevance_scorer = StoryRelevanceScorer()
story_engine = StoryEngine()
pdf_engine = PDFStorybookGenerator()

with app.app_context():
    db.create_all()


# Sample images directory
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'samples')

PRESET_SAMPLES = [
    {
        "id": "beach_sunset",
        "filename": "beach_sunset.jpg",
        "title": "Sunset Shoreline",
        "badge": "Coastline & Ocean",
        "description": "A lone child contemplating the golden sunset waves beside a wooden boat."
    },
    {
        "id": "enchanted_forest",
        "filename": "enchanted_forest.jpg",
        "title": "Whispering Woods",
        "badge": "Ancient Forest",
        "description": "Ancient moss-covered trees illuminated by sunbeams with a mythical deer."
    },
    {
        "id": "cyberpunk_city",
        "filename": "cyberpunk_city.jpg",
        "title": "Neon Metropolis",
        "badge": "Sci-Fi Urban",
        "description": "Towering futuristic skyscrapers glowing with holographic neon billboards."
    },
    {
        "id": "ancient_library",
        "filename": "ancient_library.jpg",
        "title": "The Grand Archive",
        "badge": "Historic Study",
        "description": "Towering bookshelves holding forgotten leather manuscripts under warm lamplight."
    },
    {
        "id": "mountain_summit",
        "filename": "mountain_summit.jpg",
        "title": "Alpine Peak",
        "badge": "Mountain Summit",
        "description": "A resolute mountaineer standing above a sea of clouds gazing at snowy peaks."
    },
    {
        "id": "cozy_cafe",
        "filename": "cozy_cafe.jpg",
        "title": "Rainy Day Cafe",
        "badge": "Cozy Interior",
        "description": "A steaming coffee mug and journal on a wooden table beside a rain-streaked window."
    }
]


# ===================== UI ROUTES =====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ===================== SAMPLES API =====================

@app.route('/api/samples', methods=['GET'])
def get_samples():
    return jsonify({"success": True, "samples": PRESET_SAMPLES})


# ===================== AUTH API =====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"success": False, "error": "Username or email already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    return jsonify({"success": True, "user": user.to_dict()})


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    session['user_id'] = user.id
    return jsonify({"success": True, "user": user.to_dict()})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True})


@app.route('/api/auth/me', methods=['GET'])
def current_user():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            return jsonify({"success": True, "user": user.to_dict()})
    return jsonify({"success": True, "user": None})


# ===================== PREPROCESSING & ML UNDERSTANDING =====================

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    Handles image upload or selection from preset sample gallery.
    Performs complete PyTorch preprocessing and Vision Understanding analysis.
    """
    user_id = session.get('user_id')
    sample_id = request.form.get('sample_id') or (request.json.get('sample_id') if request.is_json else None)

    target_filepath = None
    original_filename = None

    if sample_id:
        # User chose preset sample
        sample = next((s for s in PRESET_SAMPLES if s['id'] == sample_id), None)
        if not sample:
            return jsonify({"success": False, "error": "Preset sample not found"}), 404

        src_path = os.path.join(SAMPLES_DIR, sample['filename'])
        original_filename = sample['filename']
        ext = os.path.splitext(original_filename)[1]
        new_filename = f"sample_{uuid.uuid4().hex[:8]}_{original_filename}"
        target_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        shutil.copyfile(src_path, target_filepath)
    else:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image file uploaded"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"success": False, "error": "Empty filename"}), 400

        original_filename = secure_filename(file.filename or "")
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            return jsonify({"success": False, "error": "Supported formats: JPG, PNG, WEBP, BMP"}), 400

        new_filename = f"upload_{uuid.uuid4().hex[:8]}_{original_filename}"
        target_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(target_filepath)

    # 1. Run Preprocessing Pipeline (PyTorch Normalize + Quality Diagnostics)
    try:
        tensor, diagnostics, pil_img = preprocessor.preprocess(target_filepath)
    except Exception as e:
        return jsonify({"success": False, "error": f"Preprocessing error: {str(e)}"}), 500

    # 2. Run Vision Model Understanding
    try:
        vision_metadata = vision_engine.analyze_image(tensor, diagnostics, pil_img, filename=original_filename)
    except Exception as e:
        return jsonify({"success": False, "error": f"Vision model error: {str(e)}"}), 500

    # 3. Store in DB
    relative_filepath = f"/uploads/{os.path.basename(target_filepath)}"
    image_record = ImageUpload(
        user_id=user_id,
        filename=original_filename,
        filepath=relative_filepath,
        scene_category=vision_metadata.get("scene_category"),
        detected_objects_json=json.dumps(vision_metadata.get("detected_objects", [])),
        caption=vision_metadata.get("generated_caption"),
        diagnostics_json=json.dumps(diagnostics)
    )
    db.session.add(image_record)
    db.session.commit()

    return jsonify({
        "success": True,
        "image_id": image_record.id,
        "image_url": relative_filepath,
        "diagnostics": diagnostics,
        "vision_metadata": vision_metadata
    })


# ===================== STORY GENERATION =====================

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """
    Generate structured story using visual metadata + user parameters.
    """
    user_id = session.get('user_id')
    data = request.get_json() or {}

    image_id = data.get('image_id')
    genre = data.get('genre', 'Adventure')
    length = data.get('length', 'Medium')
    tone = data.get('tone', 'Emotional')
    ending = data.get('ending', 'Happy')
    custom_character = data.get('custom_character') # e.g. {"name": "Arjun"}
    api_key = data.get('api_key')

    image_record = db.session.get(ImageUpload, image_id) if image_id else None
    if not image_record:
        return jsonify({"success": False, "error": "Valid image_id is required"}), 400

    vision_metadata = {
        "scene_category": image_record.scene_category,
        "detected_objects": image_record.get_detected_objects(),
        "generated_caption": image_record.caption,
        "lighting_atmosphere": "Golden Sunset / Ambient Glow",
        "ambient_mood": "Tranquil & Atmospheric"
    }

    # 1. Generate Story
    story_data = story_engine.generate_story(
        vision_metadata=vision_metadata,
        genre=genre,
        length=length,
        tone=tone,
        ending=ending,
        custom_character=custom_character,
        api_key=api_key
    )

    # 2. Evaluate Story Relevance Score
    relevance_data = relevance_scorer.evaluate(vision_metadata, story_data)

    # 3. Save to DB
    story_record = Story(
        user_id=user_id,
        image_id=image_record.id,
        title=story_data.get("title", "The Journey Beyond"),
        genre=genre,
        length_mode=length,
        tone=tone,
        ending=ending,
        story_json=json.dumps(story_data),
        relevance_json=json.dumps(relevance_data),
        relevance_score=relevance_data.get("overall_relevance_score", 90.0)
    )
    db.session.add(story_record)
    db.session.commit()

    return jsonify({
        "success": True,
        "story_id": story_record.id,
        "story": story_data,
        "relevance": relevance_data,
        "image_url": image_record.filepath
    })


# ===================== STORY REGENERATION / EDITING =====================

@app.route('/api/regenerate-story', methods=['POST'])
def regenerate_story():
    data = request.get_json() or {}
    story_id = data.get('story_id')
    story_record = db.session.get(Story, story_id)
    if not story_record:
        return jsonify({"success": False, "error": "Story not found"}), 404

    image_record = story_record.image_upload
    vision_metadata = {
        "scene_category": image_record.scene_category,
        "detected_objects": image_record.get_detected_objects(),
        "generated_caption": image_record.caption,
        "lighting_atmosphere": "Golden Sunset / Ambient Glow",
        "ambient_mood": "Tranquil & Atmospheric"
    }

    genre = data.get('genre', story_record.genre)
    length = data.get('length', story_record.length_mode)
    tone = data.get('tone', story_record.tone)
    ending = data.get('ending', story_record.ending)
    custom_char = data.get('custom_character')
    api_key = data.get('api_key')

    updated_story = story_engine.generate_story(
        vision_metadata=vision_metadata,
        genre=genre,
        length=length,
        tone=tone,
        ending=ending,
        custom_character=custom_char,
        api_key=api_key
    )

    relevance_data = relevance_scorer.evaluate(vision_metadata, updated_story)

    # Update record
    story_record.title = updated_story.get("title")
    story_record.genre = genre
    story_record.length_mode = length
    story_record.tone = tone
    story_record.ending = ending
    story_record.story_json = json.dumps(updated_story)
    story_record.relevance_json = json.dumps(relevance_data)
    story_record.relevance_score = relevance_data.get("overall_relevance_score", 90.0)
    db.session.commit()

    return jsonify({
        "success": True,
        "story_id": story_record.id,
        "story": updated_story,
        "relevance": relevance_data,
        "image_url": image_record.filepath
    })


# ===================== MULTI-VERSION ARENA =====================

@app.route('/api/multi-versions', methods=['POST'])
def multi_versions():
    """
    Generate 3 distinct versions for side-by-side comparison.
    """
    data = request.get_json() or {}
    image_id = data.get('image_id')
    genres = data.get('genres', ['Adventure', 'Mystery', 'Inspirational'])
    length = data.get('length', 'Medium')
    api_key = data.get('api_key')

    image_record = db.session.get(ImageUpload, image_id)
    if not image_record:
        return jsonify({"success": False, "error": "Image not found"}), 404

    vision_metadata = {
        "scene_category": image_record.scene_category,
        "detected_objects": image_record.get_detected_objects(),
        "generated_caption": image_record.caption,
        "lighting_atmosphere": "Golden Sunset / Ambient Glow",
        "ambient_mood": "Dynamic"
    }

    versions = []
    for g in genres[:3]:
        tone = "Emotional" if g == "Inspirational" else ("Suspenseful" if g == "Mystery" else "Dramatic")
        st = story_engine.generate_story(
            vision_metadata=vision_metadata,
            genre=g,
            length=length,
            tone=tone,
            ending="Unexpected" if g == "Mystery" else "Happy",
            api_key=api_key
        )
        rel = relevance_scorer.evaluate(vision_metadata, st)
        versions.append({
            "genre": g,
            "tone": tone,
            "story": st,
            "relevance": rel
        })

    return jsonify({"success": True, "versions": versions})


# ===================== STORY LIBRARY / HISTORY =====================

@app.route('/api/stories', methods=['GET'])
def list_stories():
    user_id = session.get('user_id')
    query = Story.query
    if user_id:
        # Show user's stories or all if none
        stories = query.order_by(Story.created_at.desc()).limit(30).all()
    else:
        stories = query.order_by(Story.created_at.desc()).limit(30).all()

    return jsonify({
        "success": True,
        "stories": [s.to_dict() for s in stories]
    })


@app.route('/api/stories/<int:story_id>', methods=['GET'])
def get_story_detail(story_id):
    story = db.get_or_404(Story, story_id)
    return jsonify({"success": True, "story": story.to_dict()})


@app.route('/api/stories/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    story = db.get_or_404(Story, story_id)
    db.session.delete(story)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/api/stories/<int:story_id>/favorite', methods=['POST'])
def toggle_favorite(story_id):
    story = db.get_or_404(Story, story_id)
    story.is_favorite = not story.is_favorite
    db.session.commit()
    return jsonify({"success": True, "is_favorite": story.is_favorite})


# ===================== PDF EXPORT =====================

@app.route('/api/export-pdf/<int:story_id>', methods=['GET'])
def export_pdf(story_id):
    story_record = db.get_or_404(Story, story_id)
    story_data = story_record.get_story_data()
    relevance_data = story_record.get_relevance_data()

    # Image absolute path
    image_rel = story_record.image_upload.filepath if story_record.image_upload else ""
    local_img_path = None
    if image_rel:
        clean_name = os.path.basename(image_rel)
        candidate = os.path.join(app.config['UPLOAD_FOLDER'], clean_name)
        if os.path.exists(candidate):
            local_img_path = candidate

    try:
        pdf_bytes = pdf_engine.generate_pdf(story_data, local_img_path, relevance_data)
        safe_title = "".join(c for c in story_data.get('title', 'story') if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"VisionStory_{safe_title.replace(' ', '_')}.pdf"
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"PDF Generation failed: {str(e)}"}), 500


if __name__ == '__main__':
    print("Starting VisionStory AI Server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
