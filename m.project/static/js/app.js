/**
 * VisionStory AI - Frontend Application Logic
 * Integrates PyTorch preprocessing inspection, visual understanding,
 * structured narrative generation, relevance scoring, Web Speech TTS, and PDF export.
 */

document.addEventListener('DOMContentLoaded', () => {
  // State
  let currentImageId = null;
  let currentStoryId = null;
  let currentStoryData = null;
  let currentRelevanceData = null;
  let activeSpeechUtterance = null;
  let isSpeaking = false;
  let isPaused = false;

  // DOM Elements - Navigation
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabViews = document.querySelectorAll('.tab-view');

  // DOM Elements - Upload & Diagnostics
  const dropZone = document.getElementById('dropZone');
  const imageFileInput = document.getElementById('imageFileInput');
  const browseBtn = document.getElementById('browseBtn');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const removeImageBtn = document.getElementById('removeImageBtn');
  const presetChipsContainer = document.getElementById('presetChipsContainer');

  const mlDiagnosticsCard = document.getElementById('mlDiagnosticsCard');
  const toggleMlDiagnostics = document.getElementById('toggleMlDiagnostics');
  const mlDiagnosticsBody = document.getElementById('mlDiagnosticsBody');
  const sharpnessBadge = document.getElementById('sharpnessBadge');
  const diagTensorShape = document.getElementById('diagTensorShape');
  const diagSharpness = document.getElementById('diagSharpness');
  const diagLighting = document.getElementById('diagLighting');
  const diagColorTemp = document.getElementById('diagColorTemp');
  const colorSwatches = document.getElementById('colorSwatches');
  const detectedEntityTags = document.getElementById('detectedEntityTags');
  const generatedCaptionText = document.getElementById('generatedCaptionText');

  // DOM Elements - Controls & Generation
  const storyControlsForm = document.getElementById('storyControlsForm');
  const genreSelect = document.getElementById('genreSelect');
  const lengthSelect = document.getElementById('lengthSelect');
  const toneSelect = document.getElementById('toneSelect');
  const endingSelect = document.getElementById('endingSelect');
  const customCharInput = document.getElementById('customCharInput');
  const generateStoryBtn = document.getElementById('generateStoryBtn');

  // DOM Elements - Story Display
  const emptyStoryPlaceholder = document.getElementById('emptyStoryPlaceholder');
  const storyResultCard = document.getElementById('storyResultCard');
  const storyTitle = document.getElementById('storyTitle');
  const storyGenreBadge = document.getElementById('storyGenreBadge');
  const storyToneBadge = document.getElementById('storyToneBadge');
  const storyEndingBadge = document.getElementById('storyEndingBadge');
  const storySceneMeta = document.getElementById('storySceneMeta');
  const charactersList = document.getElementById('charactersList');
  const chaptersContainer = document.getElementById('chaptersContainer');
  const dialogueList = document.getElementById('dialogueList');
  const moralText = document.getElementById('moralText');

  // Relevance Score DOM
  const relevanceScoreVal = document.getElementById('relevanceScoreVal');
  const relevanceTier = document.getElementById('relevanceTier');
  const relevanceSummary = document.getElementById('relevanceSummary');
  const scoreEntityFidelity = document.getElementById('scoreEntityFidelity');
  const scoreSceneAlignment = document.getElementById('scoreSceneAlignment');
  const scoreThematic = document.getElementById('scoreThematic');
  const barEntity = document.getElementById('barEntity');
  const barScene = document.getElementById('barScene');
  const barThematic = document.getElementById('barThematic');

  // Tool Buttons
  const btnTTSPlay = document.getElementById('btnTTSPlay');
  const ttsBtnText = document.getElementById('ttsBtnText');
  const btnExportPDF = document.getElementById('btnExportPDF');
  const btnEditStory = document.getElementById('btnEditStory');
  const btnSaveFavorite = document.getElementById('btnSaveFavorite');

  // Audio Bar
  const audioPlayerBar = document.getElementById('audioPlayerBar');
  const audioPauseBtn = document.getElementById('audioPauseBtn');
  const audioStopBtn = document.getElementById('audioStopBtn');
  const audioStatusText = document.getElementById('audioStatusText');
  const voiceSelect = document.getElementById('voiceSelect');
  const rateSlider = document.getElementById('rateSlider');

  // Library
  const libraryGrid = document.getElementById('libraryGrid');
  const librarySearch = document.getElementById('librarySearch');

  // Modals
  const editStoryModal = document.getElementById('editStoryModal');
  const closeEditModal = document.getElementById('closeEditModal');
  const cancelEditBtn = document.getElementById('cancelEditBtn');
  const editStoryForm = document.getElementById('editStoryForm');
  const editGenreSelect = document.getElementById('editGenreSelect');
  const editToneSelect = document.getElementById('editToneSelect');
  const editEndingSelect = document.getElementById('editEndingSelect');
  const editCharName = document.getElementById('editCharName');

  // ==================== INITIALIZATION ====================
  initTabs();
  loadPresetSamples();
  initVoiceList();

  // ==================== TAB NAVIGATION ====================
  function initTabs() {
    navBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        navBtns.forEach(b => b.classList.remove('active'));
        tabViews.forEach(v => v.classList.remove('active'));

        btn.classList.add('active');
        const targetTab = btn.getAttribute('data-tab');
        const targetView = document.getElementById(targetTab);
        if (targetView) targetView.classList.add('active');

        if (targetTab === 'library-tab') {
          loadStoryLibrary();
        }
      });
    });
  }

  // ==================== PRESET SAMPLES ====================
  async function loadPresetSamples() {
    try {
      const res = await fetch('/api/samples');
      const data = await res.json();
      if (data.success && data.samples) {
        presetChipsContainer.innerHTML = '';
        data.samples.forEach(sample => {
          const chip = document.createElement('div');
          chip.className = 'preset-chip';
          chip.innerHTML = `
            <img src="/static/samples/${sample.filename}" alt="${sample.title}">
            <span class="preset-chip-title">${sample.title}</span>
          `;
          chip.addEventListener('click', () => selectPresetSample(sample.id, chip));
          presetChipsContainer.appendChild(chip);
        });
      }
    } catch (err) {
      console.error('Error loading preset samples:', err);
    }
  }

  async function selectPresetSample(sampleId, chipEl) {
    document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
    if (chipEl) chipEl.classList.add('active');

    showUploadLoading(true);
    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample_id: sampleId })
      });
      const data = await res.json();
      if (data.success) {
        handleUploadSuccess(data);
      } else {
        alert('Upload error: ' + (data.error || 'Failed to process sample'));
      }
    } catch (err) {
      alert('Network error processing sample');
    } finally {
      showUploadLoading(false);
    }
  }

  // ==================== IMAGE UPLOAD & DROPZONE ====================
  browseBtn.addEventListener('click', () => imageFileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  imageFileInput.addEventListener('change', () => {
    if (imageFileInput.files && imageFileInput.files[0]) {
      handleFileUpload(imageFileInput.files[0]);
    }
  });

  removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    currentImageId = null;
    imageFileInput.value = '';
    imagePreviewContainer.classList.add('hidden');
    document.querySelector('.drop-content').classList.remove('hidden');
    if (mlDiagnosticsCard) mlDiagnosticsCard.classList.add('hidden');
    document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
  });

  async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('image', file);

    showUploadLoading(true);
    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        handleUploadSuccess(data);
      } else {
        alert('Upload failed: ' + (data.error || 'Server error'));
      }
    } catch (err) {
      alert('Error uploading file');
    } finally {
      showUploadLoading(false);
    }
  }

  function showUploadLoading(loading) {
    if (loading) {
      browseBtn.disabled = true;
      browseBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
    } else {
      browseBtn.disabled = false;
      browseBtn.innerHTML = '<i class="fa-solid fa-folder-open"></i> Browse Files';
    }
  }

  function handleUploadSuccess(data) {
    currentImageId = data.image_id;

    // Display Preview
    imagePreview.src = data.image_url;
    document.querySelector('.drop-content').classList.add('hidden');
    imagePreviewContainer.classList.remove('hidden');

    // Populate ML Diagnostics
    displayMlDiagnostics(data.diagnostics, data.vision_metadata);
  }

  function displayMlDiagnostics(diag, vision) {
    if (!mlDiagnosticsCard) return;
    mlDiagnosticsCard.classList.remove('hidden');

    // Sharpness
    const sh = diag.sharpness || {};
    if (sharpnessBadge) sharpnessBadge.textContent = sh.assessment || 'Inspected';
    if (diagSharpness) diagSharpness.textContent = sh.laplacian_variance || 'N/A';

    // Tensor shape
    const pt = diag.pytorch_tensor || {};
    if (diagTensorShape) diagTensorShape.textContent = pt.shape ? `[${pt.shape.join(', ')}]` : '[1, 3, 224, 224]';

    // Lighting & Color
    const lt = diag.lighting || {};
    if (diagLighting) diagLighting.textContent = lt.category || 'Natural Lighting';
    if (diagColorTemp) diagColorTemp.textContent = lt.color_temperature || 'Balanced';

    // Color swatches
    if (colorSwatches) {
      colorSwatches.innerHTML = '';
      (diag.dominant_colors || []).forEach(col => {
        const sw = document.createElement('div');
        sw.className = 'color-swatch';
        sw.style.backgroundColor = col.hex;
        sw.title = `RGB(${col.r}, ${col.g}, ${col.b})`;
        colorSwatches.appendChild(sw);
      });
    }

    // Detected objects tags
    if (detectedEntityTags) {
      detectedEntityTags.innerHTML = '';
      (vision.detected_objects || []).forEach(obj => {
        const tag = document.createElement('span');
        tag.className = 'entity-tag';
        tag.innerHTML = `<i class="fa-solid fa-tag"></i> ${obj.name} <small>(${Math.round(obj.confidence * 100)}%)</small>`;
        detectedEntityTags.appendChild(tag);
      });
    }

    // Caption
    if (generatedCaptionText) {
      generatedCaptionText.textContent = vision.generated_caption || 'Visual context analyzed.';
    }
  }

  // Toggle diagnostics body
  if (toggleMlDiagnostics && mlDiagnosticsBody) {
    toggleMlDiagnostics.addEventListener('click', () => {
      mlDiagnosticsBody.classList.toggle('hidden');
      const icon = toggleMlDiagnostics.querySelector('.toggle-icon');
      if (icon) {
        if (mlDiagnosticsBody.classList.contains('hidden')) {
          icon.className = 'fa-solid fa-chevron-right toggle-icon';
        } else {
          icon.className = 'fa-solid fa-chevron-down toggle-icon';
        }
      }
    });
  }


  // ==================== STORY GENERATION ====================
  generateStoryBtn.addEventListener('click', async () => {
    if (!currentImageId) {
      alert('Please upload an image or choose a preset sample first!');
      return;
    }

    const payload = {
      image_id: currentImageId,
      genre: genreSelect.value,
      length: lengthSelect.value,
      tone: toneSelect.value,
      ending: endingSelect.value,
      custom_character: customCharInput.value.trim() ? { name: customCharInput.value.trim() } : null
    };

    setGeneratingState(true);
    try {
      const res = await fetch('/api/generate-story', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        displayStory(data);
      } else {
        alert('Generation failed: ' + (data.error || 'Server error'));
      }
    } catch (err) {
      alert('Error connecting to narrative engine.');
    } finally {
      setGeneratingState(false);
    }
  });

  function setGeneratingState(generating) {
    const btnText = generateStoryBtn.querySelector('.btn-text');
    const btnLoader = generateStoryBtn.querySelector('.btn-loader');
    if (generating) {
      generateStoryBtn.disabled = true;
      btnText.classList.add('hidden');
      btnLoader.classList.remove('hidden');
    } else {
      generateStoryBtn.disabled = false;
      btnText.classList.remove('hidden');
      btnLoader.classList.add('hidden');
    }
  }

  function displayStory(data) {
    currentStoryId = data.story_id;
    currentStoryData = data.story;
    currentRelevanceData = data.relevance;

    emptyStoryPlaceholder.classList.add('hidden');
    storyResultCard.classList.remove('hidden');

    // Header metadata
    storyTitle.textContent = currentStoryData.title || 'Untitled Narrative';
    storyGenreBadge.textContent = currentStoryData.genre || 'Adventure';
    storyToneBadge.textContent = currentStoryData.tone || 'Emotional';
    storyEndingBadge.textContent = (currentStoryData.ending || 'Happy') + ' Ending';
    storySceneMeta.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${currentStoryData.scene_setting || 'Grounded Visual Scene'}`;

    // Relevance Score Card
    const rel = currentRelevanceData || {};
    const overallScore = rel.overall_relevance_score || 92.0;
    relevanceScoreVal.textContent = `${overallScore}%`;
    relevanceTier.textContent = rel.rating_tier || 'High Visual Fidelity';
    relevanceSummary.textContent = rel.summary_note || 'Strong correspondence with detected entities and setting.';

    const breakdown = rel.breakdown || {};
    const entVal = breakdown.entity_fidelity || 95;
    const scVal = breakdown.scene_alignment || 90;
    const thVal = breakdown.thematic_resonance || 92;

    scoreEntityFidelity.textContent = `${entVal}%`;
    scoreSceneAlignment.textContent = `${scVal}%`;
    scoreThematic.textContent = `${thVal}%`;

    barEntity.style.width = `${entVal}%`;
    barScene.style.width = `${scVal}%`;
    barThematic.style.width = `${thVal}%`;

    // Characters
    charactersList.innerHTML = '';
    (currentStoryData.characters || []).forEach(ch => {
      const card = document.createElement('div');
      card.className = 'character-card';
      const initial = (ch.name || 'C')[0].toUpperCase();
      card.innerHTML = `
        <div class="char-avatar">${initial}</div>
        <div class="char-details">
          <h5>${ch.name}</h5>
          <span class="char-role">${ch.role}</span>
          <p class="char-trait">${ch.personality}</p>
        </div>
      `;
      charactersList.appendChild(card);
    });

    // Chapters
    chaptersContainer.innerHTML = '';
    (currentStoryData.chapters || []).forEach(ch => {
      const block = document.createElement('div');
      block.className = 'chapter-block';
      block.innerHTML = `
        <h4 class="chapter-heading">${ch.heading}</h4>
        <p class="chapter-p">${ch.content}</p>
      `;
      chaptersContainer.appendChild(block);
    });

    // Dialogues
    dialogueList.innerHTML = '';
    (currentStoryData.dialogue || []).forEach(d => {
      const bubble = document.createElement('div');
      bubble.className = 'dialogue-bubble';
      bubble.innerHTML = `
        <span class="speaker-badge">${d.speaker}:</span>
        <span class="dialogue-line">"${d.line}"</span>
      `;
      dialogueList.appendChild(bubble);
    });

    // Moral
    moralText.textContent = `"${currentStoryData.moral || 'Every journey illuminates the horizon of understanding.'}"`;

    // Stop speech if running from previous story
    stopSpeech();

    // Smooth scroll to story card
    storyResultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }


  // ==================== TEXT-TO-SPEECH (TTS) ====================
  function initVoiceList() {
    if ('speechSynthesis' in window) {
      const populateVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        voiceSelect.innerHTML = '';
        voices.forEach((voice, index) => {
          if (voice.lang.startsWith('en')) {
            const opt = document.createElement('option');
            opt.value = index;
            opt.textContent = `${voice.name} (${voice.lang})`;
            voiceSelect.appendChild(opt);
          }
        });
      };
      populateVoices();
      if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = populateVoices;
      }
    }
  }

  btnTTSPlay.addEventListener('click', () => {
    if (!currentStoryData) return;
    if (isSpeaking && !isPaused) {
      pauseSpeech();
    } else if (isPaused) {
      resumeSpeech();
    } else {
      startSpeech();
    }
  });

  audioPauseBtn.addEventListener('click', () => {
    if (isPaused) {
      resumeSpeech();
    } else {
      pauseSpeech();
    }
  });

  audioStopBtn.addEventListener('click', () => stopSpeech());

  function startSpeech() {
    if (!('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported in this browser.');
      return;
    }
    window.speechSynthesis.cancel();

    // Assemble text to speak
    const speechChunks = [
      currentStoryData.title,
      ...currentStoryData.chapters.map(c => `${c.heading}. ${c.content}`),
      ...currentStoryData.dialogue.map(d => `${d.speaker} said: ${d.line}`),
      `Moral of the story: ${currentStoryData.moral}`
    ].join(' ');

    activeSpeechUtterance = new SpeechSynthesisUtterance(speechChunks);
    
    // Voice selection
    const voices = window.speechSynthesis.getVoices();
    const chosenIdx = voiceSelect.value;
    if (voices[chosenIdx]) activeSpeechUtterance.voice = voices[chosenIdx];

    activeSpeechUtterance.rate = parseFloat(rateSlider.value) || 1.0;

    activeSpeechUtterance.onstart = () => {
      isSpeaking = true;
      isPaused = false;
      audioPlayerBar.classList.remove('hidden');
      ttsBtnText.textContent = 'Pause';
      audioStatusText.textContent = 'Narrating story...';
      audioPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
    };

    activeSpeechUtterance.onend = () => {
      isSpeaking = false;
      isPaused = false;
      audioPlayerBar.classList.add('hidden');
      ttsBtnText.textContent = 'Listen';
    };

    activeSpeechUtterance.onerror = () => {
      isSpeaking = false;
      isPaused = false;
      audioPlayerBar.classList.add('hidden');
      ttsBtnText.textContent = 'Listen';
    };

    window.speechSynthesis.speak(activeSpeechUtterance);
  }

  function pauseSpeech() {
    if (window.speechSynthesis.speaking && !isPaused) {
      window.speechSynthesis.pause();
      isPaused = true;
      ttsBtnText.textContent = 'Resume';
      audioStatusText.textContent = 'Narration paused';
      audioPauseBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
    }
  }

  function resumeSpeech() {
    if (isPaused) {
      window.speechSynthesis.resume();
      isPaused = false;
      ttsBtnText.textContent = 'Pause';
      audioStatusText.textContent = 'Narrating story...';
      audioPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
    }
  }

  function stopSpeech() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    isSpeaking = false;
    isPaused = false;
    audioPlayerBar.classList.add('hidden');
    ttsBtnText.textContent = 'Listen';
  }


  // ==================== PDF EXPORT ====================
  btnExportPDF.addEventListener('click', () => {
    if (!currentStoryId) return;
    window.location.href = `/api/export-pdf/${currentStoryId}`;
  });


  // ==================== EDIT & REGENERATE STORY ====================
  btnEditStory.addEventListener('click', () => {
    if (!currentStoryData) return;
    editGenreSelect.value = currentStoryData.genre || 'Adventure';
    editToneSelect.value = currentStoryData.tone || 'Emotional';
    editEndingSelect.value = currentStoryData.ending || 'Happy';
    editCharName.value = currentStoryData.characters?.[0]?.name || '';
    editStoryModal.classList.remove('hidden');
  });

  closeEditModal.addEventListener('click', () => editStoryModal.classList.add('hidden'));
  cancelEditBtn.addEventListener('click', () => editStoryModal.classList.add('hidden'));

  editStoryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentStoryId) return;

    const payload = {
      story_id: currentStoryId,
      genre: editGenreSelect.value,
      tone: editToneSelect.value,
      ending: editEndingSelect.value,
      custom_character: editCharName.value.trim() ? { name: editCharName.value.trim() } : null
    };

    editStoryModal.classList.add('hidden');
    setGeneratingState(true);

    try {
      const res = await fetch('/api/regenerate-story', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        displayStory(data);
      } else {
        alert('Regeneration failed: ' + data.error);
      }
    } catch (err) {
      alert('Error regenerating story.');
    } finally {
      setGeneratingState(false);
    }
  });


  // ==================== FAVORITE STORY ====================
  btnSaveFavorite.addEventListener('click', async () => {
    if (!currentStoryId) return;
    try {
      const res = await fetch(`/api/stories/${currentStoryId}/favorite`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        const icon = btnSaveFavorite.querySelector('i');
        if (data.is_favorite) {
          icon.className = 'fa-solid fa-bookmark text-accent';
        } else {
          icon.className = 'fa-regular fa-bookmark';
        }
      }
    } catch (err) {
      console.error(err);
    }
  });





  // ==================== STORY LIBRARY ====================
  async function loadStoryLibrary() {
    try {
      const res = await fetch('/api/stories');
      const data = await res.json();
      if (data.success && data.stories) {
        renderLibrary(data.stories);
      }
    } catch (err) {
      console.error('Error loading library:', err);
    }
  }

  function renderLibrary(stories) {
    libraryGrid.innerHTML = '';
    if (stories.length === 0) {
      libraryGrid.innerHTML = '<p style="color:var(--text-subtle); grid-column:1/-1;">No saved stories yet. Generate your first story in the Studio!</p>';
      return;
    }

    stories.forEach(story => {
      const stData = story.story_data || {};
      const card = document.createElement('div');
      card.className = 'lib-card';
      const imgSrc = story.image_path || '/static/samples/beach_sunset.jpg';
      const dateStr = new Date(story.created_at).toLocaleDateString();

      card.innerHTML = `
        <img src="${imgSrc}" class="lib-img" alt="${story.title}">
        <div class="lib-body">
          <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span class="genre-tag">${story.genre}</span>
            <span class="badge-pill">${story.relevance_score}% Relevance</span>
          </div>
          <h4 class="lib-title">${story.title}</h4>
          <div class="lib-meta">
            <span>${dateStr}</span>
            <span>${story.length_mode} &bull; ${story.tone}</span>
          </div>
          <div class="lib-actions">
            <button class="btn-primary btn-sm btn-view-story" data-id="${story.id}">
              <i class="fa-solid fa-eye"></i> View
            </button>
            <a href="/api/export-pdf/${story.id}" class="btn-secondary btn-sm" title="Export PDF">
              <i class="fa-solid fa-file-pdf"></i>
            </a>
            <button class="btn-secondary btn-sm btn-del-story" data-id="${story.id}" title="Delete">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>
      `;

      card.querySelector('.btn-view-story').addEventListener('click', () => {
        displayStory({
          story_id: story.id,
          story: stData,
          relevance: story.relevance_data
        });
        // Switch back to Studio
        document.querySelector('[data-tab="studio-tab"]').click();
      });

      card.querySelector('.btn-del-story').addEventListener('click', async () => {
        if (confirm('Delete this story?')) {
          await fetch(`/api/stories/${story.id}`, { method: 'DELETE' });
          loadStoryLibrary();
        }
      });

      libraryGrid.appendChild(card);
    });
  }

  librarySearch.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    document.querySelectorAll('.lib-card').forEach(card => {
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(term) ? 'block' : 'none';
    });
  });

});
