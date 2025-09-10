# Caroline Praise Loop App

A minimalist Flask web app to help with dog separation anxiety. Record your voice, and the app will play randomized praise clips in an infinite loop.

---

## Features

- **In-Browser Recording:** No need for audio files. Record, save, and manage praise clips directly in the app.
- **CRUD Management:** Play, rename, and delete individual phrases.
- **Randomized Loop:** Plays a random clip from your list continuously.
- **Customizable Pauses:** Set a minimum and maximum pause duration between clips.
- **Modern UI:** A clean, easy-to-use interface for managing your recordings.
- **Fully Offline/Local:** Works entirely on your local machine. No cloud services, analytics, or internet required.

---

## Directory Structure

```
.
├── dog_praise_loop_app.py  # The main Flask application
└── phrases/                  # Auto-generated folder for your recorded audio clips
```

---

## Setup Instructions

**1. Install Dependencies**

This app requires `ffmpeg`. If you don't have it, install it first.

*On macOS (using Homebrew):*
```bash
brew install ffmpeg
```

Then, install the required Python libraries:

```bash
pip install flask pydub
```

**2. Run the App**

```bash
python dog_praise_loop_app.py
```

By default, the app runs on `http://localhost:5050`.

---

## How to Use

1.  **Record a Phrase:**
    *   Click the "Record" button.
    *   Click "Stop" when you're finished. The recording will be saved automatically.

2.  **Manage Phrases:**
    *   Click the "Manage Phrases" button to see your list of recordings.
    *   You can **Play** (▶️), **Rename** (✏️), or **Delete** (🗑️) any phrase.

3.  **Start the Loop:**
    *   Click "Start Loop". The app will begin playing random phrases from your list.
    *   You can adjust the minimum and maximum pause times in the "Loop Settings" section.
    *   Click "Stop Loop" to end the playback.

---

## Future Features

- **Speech-to-Text for Automatic Naming:** A potential feature is to use a speech-to-text library to automatically name the recorded files based on their content (e.g., `good_girl.wav`). This would be a complex addition and may require either an internet connection for cloud-based services or a difficult local setup.

---

Made for Caroline. Good dog.
