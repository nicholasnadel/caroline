# Caroline Praise Loop App

A minimalist application to help with dog separation anxiety. Available in both web and CLI versions - record your voice, and the app will play randomized praise clips in an infinite loop.

---

## Two Versions Available

### 🌐 Web Version (`dog_praise_loop_app.py`)
- Full-featured Flask web app with recording interface
- In-browser recording, playback, and management
- Modern UI for managing recordings
- Works great when you need to record new phrases

### ⚡ CLI Version (`praise_loop_cli.py`) 
- Lightweight command-line version
- Ultra-reliable playback (no browser restrictions)
- Perfect for continuous background praise loops
- Simple arguments for intervals and directories

---

## Features

### Web Version Features:
- **In-Browser Recording:** Record, save, and manage praise clips directly in the app
- **CRUD Management:** Play, rename, and delete individual phrases  
- **Randomized Loop:** Plays random clips with robust error recovery
- **Customizable Pauses:** Set minimum and maximum pause duration between clips
- **Modern UI:** Clean, easy-to-use interface for managing recordings
- **Auto-Recovery:** Automatically handles browser throttling and playback issues

### CLI Version Features:
- **System Audio:** Uses native audio playback (no browser restrictions)
- **Bulletproof Reliability:** Never affected by tab throttling or autoplay policies
- **Flexible Arguments:** Customize intervals and source directory
- **Cross-Platform:** Works on macOS, Linux, and Windows
- **Automatic Filtering:** Skips corrupted files automatically
- **Lightweight:** Minimal resource usage, perfect for background operation

---

## Directory Structure

```
.
├── dog_praise_loop_app.py    # Flask web application
├── praise_loop_cli.py        # Command-line version  
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

**2. Choose Your Version:**

### Web Version
```bash
python dog_praise_loop_app.py
```
Then visit `http://localhost:5050` in your browser.

### CLI Version  
```bash
# Default: 2-10 second intervals
python3 praise_loop_cli.py

# Custom intervals: 5-15 seconds
python3 praise_loop_cli.py --min 5 --max 15

# Very frequent praise: 1-3 seconds  
python3 praise_loop_cli.py --min 1 --max 3

# List available files
python3 praise_loop_cli.py --list

# Use different directory
python3 praise_loop_cli.py --dir ./my_sounds
```

---

## How to Use

### Web Version:
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

### CLI Version:
1. **Record phrases first** (use web version or place `.wav` files in `phrases/` directory)
2. **Run the CLI** with your desired interval settings
3. **Press Ctrl+C** to stop the loop

## Recommendations

- **For recording**: Use the web version to record and manage your phrases
- **For reliable loops**: Use the CLI version for continuous background praise  
- **Best of both**: Record with web version, then run CLI version for daily use

---

## Future Features

- **Speech-to-Text for Automatic Naming:** A potential feature is to use a speech-to-text library to automatically name the recorded files based on their content (e.g., `good_girl.wav`). This would be a complex addition and may require either an internet connection for cloud-based services or a difficult local setup.

---

Made for Caroline. Good dog.
