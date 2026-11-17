# AI – VisionStory AI: Image-Based Intelligent Story Generation System

An AI-powered multi-modal application that transforms ordinary photographs into creative, context-aware, multi-chapter storybooks using computer vision, deep learning, and natural language generation. The system analyzes uploaded images to identify objects, scenes, lighting conditions, colours, and environmental moods, then generates personalized stories containing characters, dialogues, chapters, and moral lessons.

The application combines PyTorch-based visual understanding, MobileNetV3-Small, contextual story generation, optional Google Gemini API integration, and automated PDF generation to provide a complete image-to-story creation experience.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.26-013243?style=for-the-badge&logo=numpy&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![ReportLab](https://img.shields.io/badge/ReportLab-4.x-2C3E50?style=for-the-badge)

---

# 1. Abstract

VisionStory AI is a multi-modal artificial intelligence application developed to transform ordinary photographs into creative and meaningful stories using computer vision, deep learning, and natural language generation techniques.

The system analyzes user-uploaded photographs or preset scene images to understand their visual content. It uses OpenCV for image preprocessing and quality analysis, along with PyTorch and MobileNetV3-Small for visual scene understanding and semantic classification.

The application identifies important visual elements such as objects, scene categories, lighting conditions, dominant colours, and environmental moods. These extracted visual details are passed to the story generation engine, which combines the visual information with user-selected preferences to generate personalized stories.

Users can customize the story genre, length, emotional tone, ending type, and character names. The system supports two story generation modes: a built-in contextual story generation engine that works offline and an optional Google Gemini API integration for advanced creative story generation.

The application also includes a story relevance scoring mechanism that evaluates how closely the generated story matches the uploaded image. It calculates entity fidelity, scene alignment, and thematic resonance scores to measure visual and narrative consistency.

Finally, the system generates publication-ready PDF storybooks containing the original photograph, story title, character profiles, chapters, dialogues, moral lessons, and visual relevance scores.

The main objective of this project is to demonstrate how computer vision and natural language generation can work together to transform visual information into meaningful, personalized, and creative storytelling experiences.

---

# 2. Project Overview

VisionStory AI combines computer vision, deep learning, natural language generation, and web development to create an intelligent image-to-story generation platform.

The application allows users to upload photographs or select predefined sample images from the available gallery. The uploaded image passes through an image preprocessing pipeline that checks image quality, sharpness, lighting conditions, colour temperature, and dominant colour palettes.

After preprocessing, the image is passed to a pretrained MobileNetV3-Small model for visual understanding. The system extracts semantic information such as scene categories, physical objects, environmental conditions, lighting atmosphere, and mood.

The extracted visual information is combined with user preferences to generate a structured story. Users can select different genres such as Adventure, Mystery, Science Fiction, Fantasy, Romance, Horror, Comedy, and Inspirational.

The generated stories contain titles, character profiles, multiple chapters, character dialogues, and moral lessons.

The system also provides a story relevance evaluation mechanism that checks whether the generated story accurately represents the uploaded photograph.

Users can generate multiple story versions for the same photograph, save their stories in a personal library, mark favourite stories, regenerate stories with different preferences, and export the final result as a downloadable PDF storybook.

---

# 3. Key Features

- **AI-Based Image Understanding:** Analyzes uploaded photographs using computer vision and deep learning techniques.
- **Image Upload:** Allows users to upload their own photographs for story generation.
- **Preset Scene Gallery:** Provides predefined sample images for exploring the application.
- **Image Quality Detection:** Evaluates image sharpness and blur using OpenCV Laplacian variance.
- **Lighting Analysis:** Identifies low-light, balanced natural light, and overexposed images.
- **Colour Analysis:** Extracts dominant colour palettes and determines warm or cool colour temperatures.
- **Deep Learning Scene Classification:** Uses MobileNetV3-Small to understand the visual content of images.
- **Object Identification:** Identifies important physical entities and objects present in a scene.
- **Scene Understanding:** Recognizes environments such as beaches, forests, cities, libraries, mountains, and wildlife scenes.
- **Mood Detection:** Determines the atmosphere and emotional mood associated with the image.
- **AI Story Generation:** Converts extracted visual information into creative and context-aware stories.
- **Multiple Story Genres:** Supports Adventure, Mystery, Sci-Fi, Fantasy, Romance, Horror, Comedy, and Inspirational genres.
- **Customizable Story Length:** Allows users to select Flash, Short, Medium, and Long story formats.
- **Emotional Tone Selection:** Allows users to customize the emotional tone of generated stories.
- **Custom Characters:** Supports user-defined character names and personalized character profiles.
- **Dual Story Generation Modes:** Supports an offline contextual engine and optional Google Gemini API integration.
- **Multi-Version Story Generation:** Generates three different genre-based story versions for the same photograph.
- **Story Relevance Scoring:** Evaluates how accurately the generated story represents the uploaded image.
- **Character Profiles:** Generates character names, roles, and personality descriptions.
- **Chapter-Based Storytelling:** Organizes stories into multiple acts and chapters.
- **Character Dialogues:** Generates conversations between characters.
- **Moral Lessons:** Includes meaningful moral lessons at the end of generated stories.
- **PDF Storybook Generation:** Converts generated stories into professionally formatted PDF documents.
- **Story Library:** Stores previously generated stories for future access.
- **Favourite Stories:** Allows users to mark and manage their favourite stories.
- **Story Regeneration:** Allows users to generate alternative stories using different creative preferences.
- **User Authentication:** Supports account registration and login.
- **Session Management:** Maintains user-specific story and library information.

---

# 4. AI & Machine Learning Algorithms

The project uses computer vision, deep learning, semantic classification, contextual natural language generation, and mathematical relevance evaluation techniques.

| Algorithm / Model | Purpose |
|---|---|
| MobileNetV3-Small | Identifies visual features and classifies image content |
| CNN | Extracts important visual features from images |
| ImageNet Classification | Provides pretrained visual categories and predictions |
| Softmax Classification | Converts model outputs into class probabilities |
| Laplacian Variance | Measures image sharpness and blur |
| Colour Quantization | Extracts dominant colours from images |
| ImageNet Normalization | Prepares images for deep learning inference |
| Contextual Archetype Engine | Generates stories using detected visual information and user preferences |
| Google Gemini API | Provides optional LLM-based creative story generation |
| Entity Recall | Evaluates whether detected objects appear in the generated story |
| Scene Alignment | Measures consistency between the detected environment and story |
| Thematic Resonance | Evaluates whether the story matches the image's mood and atmosphere |

### 4.1 MobileNetV3-Small

MobileNetV3-Small is a lightweight convolutional neural network designed for efficient image classification and visual feature extraction.

In VisionStory AI, it is used to analyze uploaded photographs and identify visual categories.

The model processes a normalized image tensor and produces classification probabilities based on its pretrained ImageNet-1K categories.

The application uses the top predictions to understand the possible objects and scene characteristics present in the photograph.

**Working Process:**

1. Upload an image.
2. Preprocess and resize the image to 224 × 224 pixels.
3. Convert the image into a PyTorch tensor.
4. Apply ImageNet normalization.
5. Pass the tensor through MobileNetV3-Small.
6. Generate classification probabilities using Softmax.
7. Extract the top five predictions.
8. Map the predictions to the application's semantic scene taxonomy.

### 4.2 Convolutional Neural Network (CNN)

A Convolutional Neural Network is a deep learning model designed to process visual information.

It extracts important image features such as edges, shapes, textures, and patterns through convolutional layers.

In this project, MobileNetV3-Small uses CNN-based feature extraction to understand image content and support scene classification.

### 4.3 Laplacian Variance – Blur Detection

Laplacian Variance is an image processing technique used to determine whether an image is sharp or blurry.

The Laplacian operator detects rapid intensity changes and edges in an image.

The system calculates the variance of the Laplacian response to estimate image sharpness.

**Formula:**

\[
L(I)=\frac{\partial^2 I}{\partial x^2}
+\frac{\partial^2 I}{\partial y^2}
\]

\[
\text{Laplacian Variance}
=\frac{1}{N}\sum_{i=1}^{N}(L_i-\mu)^2
\]

**Project Classification Thresholds:**

| Variance Value | Image Quality |
|---|---|
| Above 150 | Crisp / High Detail |
| 50–150 | Acceptable Sharpness |
| 50 or below | Soft / Slight Blur |

This technique helps identify image quality before visual analysis.

### 4.4 ImageNet Normalization

ImageNet normalization prepares an image for processing by a pretrained deep learning model.

The system converts the image into a PyTorch tensor and normalizes its RGB channels using predefined ImageNet mean and standard deviation values.

**Normalization Values:**

- Mean: [0.485, 0.456, 0.406]
- Standard Deviation: [0.229, 0.224, 0.225]

**Working Process:**

1. Resize the image to 256 × 256 pixels.
2. Apply center cropping to obtain 224 × 224 pixels.
3. Convert the image into a tensor.
4. Normalize the RGB channels.
5. Add a batch dimension.
6. Pass the resulting tensor to the vision model.

The final tensor shape is:

`[1, 3, 224, 224]`

### 4.5 Colour Quantization and Colour Temperature Analysis

Colour quantization reduces the number of colours in an image and identifies its dominant colour palette.

The application resizes a copy of the image to 100 × 100 pixels and uses PIL octree quantization to extract the four dominant RGB colour values.

The system also compares red and blue channel energy to identify the overall colour temperature.

It classifies the atmosphere into categories such as:

- Warm Sunset / Golden Amber
- Cool Azure / Twilight
- Vibrant Balanced

### 4.6 Contextual Story Generation

The built-in contextual story engine generates narratives using detected objects, scene categories, lighting conditions, mood, and user-selected preferences.

It uses predefined narrative structures, character name pools, personality descriptions, and genre-based story templates.

The engine combines visual information with user preferences to produce structured stories without requiring an external AI API.

### 4.7 Google Gemini API Integration

The application optionally integrates Google Gemini API for advanced natural language generation.

When a valid API key is available, the system can use Gemini to generate more flexible and creative stories based on visual descriptions and user instructions.

When the API key is unavailable, the application uses its built-in contextual story generation engine.

### 4.8 Story Relevance Scoring

The Story Relevance Scoring Engine evaluates whether the generated story accurately represents the uploaded photograph.

It calculates three major scores:

**1. Entity Fidelity**

Checks whether objects identified in the photograph are mentioned in the generated story.

For example, if the image contains a wooden boat, ocean water, and sandy shore, the engine checks whether these entities or their synonyms appear in the story.

\[
S_{entity}=
\frac{\text{Matched Visual Entities}}
{\text{Total Detected Entities}}\times100
\]

**2. Scene Alignment**

Measures how closely the story matches the detected environment and scene category.

It compares scene-related keywords with the generated story.

\[
S_{scene}=
\min\left(100,
\frac{|W_{scene}\cap W_{story}|}
{|W_{scene}|}\times110\right)
\]

**3. Thematic Resonance**

Checks whether the story matches the emotional mood and lighting atmosphere of the photograph.

\[
S_{theme}=
\min\left(100,
\frac{|W_{mood}\cap W_{story}|}
{|W_{mood}|}\times120\right)
\]

**Overall Relevance Formula:**

\[
R=0.45S_{entity}+0.35S_{scene}+0.20S_{theme}
\]

Where:

- Entity Fidelity has a weight of 45%.
- Scene Alignment has a weight of 35%.
- Thematic Resonance has a weight of 20%.

A score of 90% or above receives the High Visual Fidelity classification.

---

# 5. Technology Stack

### Backend

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-3.1-D71F00?style=flat-square)

- Python 3.12 – Main programming language.
- Flask 3.1 – Backend web framework.
- Flask-SQLAlchemy 3.1 – Database integration and ORM.
- REST API – Handles communication between frontend and backend.

### Deep Learning & Computer Vision

![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Contrib-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.26-013243?style=flat-square&logo=numpy&logoColor=white)

- PyTorch 2.x – Deep learning and neural network inference.
- Torchvision – Image transformations and pretrained models.
- MobileNetV3-Small – Visual classification.
- OpenCV (opencv-contrib-python) – Image preprocessing and diagnostics.
- NumPy 1.26 – Numerical computations.
- Pillow (PIL) – Image manipulation and colour quantization.

### Story Generation

- Contextual Archetype Engine – Offline story generation.
- Google Gemini API – Optional LLM-based story generation.
- Natural Language Generation – Converts visual information into structured narratives.

### PDF Generation

![ReportLab](https://img.shields.io/badge/ReportLab-4.x-2C3E50?style=flat-square)

- ReportLab 4.x – PDF document generation.
- Platypus – Page layout and document formatting.
- Custom Typography – Storybook formatting and character sections.

### Frontend

- HTML5 – Web application structure.
- CSS3 – Styling and dark-theme glassmorphism interface.
- Vanilla JavaScript – Client-side functionality and API communication.
- Font Awesome – Icons and visual elements.

### Database

![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)

- SQLite – Stores user accounts, image uploads, stories, story versions, relevance scores, and favourite information.
- SQLAlchemy – Manages database models and queries.

---

# 6. System Architecture

VisionStory AI follows a modular multi-layer architecture that connects image preprocessing, computer vision, natural language generation, relevance evaluation, and PDF publication.

**1. Frontend Layer**

The frontend is developed using HTML5, CSS3, and Vanilla JavaScript. It provides the user interface for image uploads, preset image selection, story customization, story viewing, and library management.

**2. Backend Layer**

The backend is developed using Python and Flask. It handles user requests, application logic, API endpoints, image processing coordination, story generation, and database operations.

**3. Image Preprocessing Layer**

OpenCV, Pillow, and PyTorch Torchvision are used to analyze image quality, detect blur, calculate lighting conditions, extract dominant colours, and convert images into normalized tensors.

**4. Computer Vision Layer**

MobileNetV3-Small processes the uploaded image and generates visual classification predictions. A semantic taxonomy maps predictions and image characteristics into scene categories, physical entities, lighting descriptions, and emotional moods.

**5. Story Generation Layer**

The story engine combines extracted visual information with user-selected genre, length, tone, ending type, and custom character names. It uses either the built-in contextual engine or optional Google Gemini API integration.

**6. Relevance Evaluation Layer**

The relevance scorer evaluates the generated narrative using Entity Fidelity, Scene Alignment, and Thematic Resonance to calculate an overall visual relevance percentage.

**7. Database Layer**

SQLite with Flask-SQLAlchemy stores user accounts, uploaded images, generated stories, story versions, relevance scores, and favourite records.

**8. PDF Generation Layer**

ReportLab generates downloadable storybooks containing cover artwork, source photographs, character profiles, chapters, dialogue sections, moral lessons, and relevance scores.

### Overall System Workflow

1. User uploads a photograph or selects a preset image.
2. The image passes through the preprocessing pipeline.
3. OpenCV checks image sharpness, lighting, and colour information.
4. PyTorch normalizes the image and prepares the tensor.
5. MobileNetV3-Small identifies visual features and scene categories.
6. The semantic taxonomy extracts objects, environment, lighting, and mood.
7. The user selects story preferences.
8. The story engine generates a structured narrative.
9. The relevance scorer compares the story with the detected image information.
10. The generated story and relevance results are stored in SQLite.
11. The user can view, regenerate, compare, or favourite stories.
12. ReportLab generates the final downloadable PDF storybook.

---

# 7. Main Project Modules

1. **User Authentication Module** – Handles user registration, login, and account management.

2. **Image Upload Module** – Allows users to upload photographs and select predefined sample images.

3. **Image Preprocessing Module** – Performs blur detection, brightness analysis, colour temperature evaluation, and image normalization.

4. **Vision Understanding Module** – Uses MobileNetV3-Small to identify visual information and classify image content.

5. **Semantic Scene Taxonomy Module** – Maps visual predictions into scene categories, objects, lighting conditions, and environmental moods.

6. **Story Generation Module** – Generates personalized narratives using the built-in contextual engine or optional Gemini API.

7. **Story Customization Module** – Allows users to select genres, story length, emotional tone, ending types, and custom character names.

8. **Multi-Version Story Module** – Generates three different genre-based story versions for the same photograph.

9. **Story Relevance Scoring Module** – Calculates Entity Fidelity, Scene Alignment, and Thematic Resonance scores.

10. **PDF Generation Module** – Converts generated stories into publication-ready PDF storybooks.

11. **Story Library Module** – Stores and displays previously generated stories.

12. **Favourite Management Module** – Allows users to save and manage favourite stories.

13. **Story Regeneration Module** – Generates alternative versions of existing stories using updated user preferences.

---

# 8. REST API & Data Management

The application uses REST API endpoints to connect the frontend with the backend services.

### Main API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/upload` | POST | Uploads an image and performs visual analysis |
| `/api/samples` | GET | Retrieves preset sample images |
| `/api/generate-story` | POST | Generates a new story |
| `/api/regenerate-story` | POST | Regenerates an existing story |
| `/api/multi-versions` | POST | Generates three story variations |
| `/api/stories` | GET | Retrieves previously generated stories |
| `/api/stories/<id>/favorite` | POST | Adds or removes a favourite |
| `/api/export-pdf/<id>` | GET | Generates and downloads a PDF storybook |
| `/api/auth/register` | POST | Registers a new user |
| `/api/auth/login` | POST | Authenticates an existing user |

### Database Management

The application uses SQLite through Flask-SQLAlchemy.

The main database entities include:

- **User:** Stores user account information.
- **ImageUpload:** Stores uploaded image information and associated visual metadata.
- **Story:** Stores generated story content and relevance information.
- **StoryVersion:** Maintains different versions of generated stories.

The database supports user-specific story management, saved favourites, image references, and story history.

---

# 9. Project Objectives

- Convert ordinary photographs into meaningful and creative stories.
- Integrate computer vision with natural language generation.
- Understand image content using deep learning models.
- Identify objects, scene categories, colours, lighting, and mood.
- Generate context-aware stories based on visual information.
- Provide customizable story genres, lengths, tones, and endings.
- Support both offline story generation and optional LLM integration.
- Evaluate the relationship between generated stories and uploaded photographs.
- Reduce irrelevant or visually inconsistent storytelling through relevance scoring.
- Generate professional PDF storybooks.
- Maintain a personal library of generated stories.
- Provide an interactive and user-friendly storytelling experience.

---

# 10. Future Enhancements

- Integration of advanced vision-language models for more accurate scene understanding.
- Improved object detection using dedicated object detection models.
- Support for multiple image uploads to generate connected stories.
- Addition of speech-to-story and voice narration features.
- Text-to-speech narration for generated storybooks.
- Multilingual story generation.
- Advanced character consistency across multiple chapters.
- More detailed visual relevance evaluation using semantic embeddings.
- Cloud-based storage and story synchronization.
- Social sharing of generated storybooks.
- Mobile application integration.
- Improved PDF customization with themes, illustrations, and layouts.
- Advanced story editing and collaborative storytelling.

---

# 11. Project Details

| Details | Information |
|---|---|
| Project Title | VisionStory AI – Image-Based Intelligent Story Generation System |
| Short Name | VisionStory AI |
| Project Type | Multi-Modal Artificial Intelligence Application |
| Project Domain | Computer Vision, Deep Learning and Natural Language Generation |
| Programming Language | Python 3.12 |
| Backend Framework | Flask 3.1 |
| Deep Learning Framework | PyTorch 2.x |
| Vision Model | MobileNetV3-Small |
| Image Processing | OpenCV, Pillow and NumPy |
| Story Generation | Contextual Archetype Engine and Google Gemini API |
| Database | SQLite |
| ORM | Flask-SQLAlchemy |
| PDF Generation | ReportLab 4.x |
| Frontend | HTML5, CSS3 and Vanilla JavaScript |

---

**⭐ Transform images into stories and explore the power of artificial intelligence, computer vision, and creative storytelling!**

*VisionStory AI – Where every picture has a story to tell.*
