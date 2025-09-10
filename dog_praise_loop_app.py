# Requirements:
# pip install pydub flask numpy scipy

from flask import Flask, send_file, render_template_string, jsonify, request
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import random
import os
import datetime

app = Flask(__name__)

# Output folder for split phrases
PHRASES_DIR = 'phrases'
os.makedirs(PHRASES_DIR, exist_ok=True)

# Get list of praise clips, sorted by newest first
def get_phrases():
    files = [os.path.join(PHRASES_DIR, f) for f in os.listdir(PHRASES_DIR) if f.endswith('.wav')]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return [os.path.basename(f) for f in files]

# HTML UI with user-triggered autoplay loop
HTML = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Caroline Praise Loop</title>
    <style>
        :root {
            --bg-color: #f6f6f7;
            --text-color: #1d1d1f;
            --accent-color: #007aff;
            --accent-hover-color: #0071e3;
            --destructive-color: #ff3b30;
            --destructive-hover-color: #ff453a;
            --border-color: #d2d2d7;
            --card-bg-color: #ffffff;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: flex-start; /* Align to top */
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: var(--card-bg-color);
            border-radius: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 30px;
            width: 100%;
            max-width: 500px;
            text-align: center;
        }
        h1, h2 {
            font-weight: 600;
        }
        h1 { font-size: 24px; margin-bottom: 8px; }
        h2 { font-size: 20px; margin-top: 30px; margin-bottom: 15px; border-top: 1px solid var(--border-color); padding-top: 20px;}
        p { color: #6e6e73; margin-bottom: 24px; }

        /* Main Controls */
        .main-controls button {
            color: white;
            font-size: 17px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            padding: 14px 0;
            width: 100%;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        #loopBtn.start {
            background-color: var(--accent-color);
        }
        #loopBtn.start:hover {
            background-color: var(--accent-hover-color);
        }
        #loopBtn.stop {
            background-color: var(--destructive-color);
        }
        #loopBtn.stop:hover {
            background-color: var(--destructive-hover-color);
        }

        .status {
            margin-top: 15px;
            font-size: 14px;
            color: #6e6e73;
        }
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #d2d2d7;
            margin-right: 8px;
            transition: background-color 0.3s ease;
        }
        .status-indicator.active {
            background-color: #34c759; /* Apple green */
        }

        /* Settings */
        .settings { margin-top: 20px; text-align: left; }
        .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .setting-item label { font-size: 15px; }
        .setting-item input {
            width: 70px;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            font-size: 15px;
            text-align: center;
            background-color: #f5f5f7;
        }
        .setting-item input[type="checkbox"] {
            width: auto;
            height: 20px;
            width: 20px;
            accent-color: var(--accent-color);
        }

        /* Recording */
        .recording-controls {
            display: flex; 
            gap: 10px; 
            align-items: center;
            justify-content: center;
        }
        .recording-controls button { 
            padding: 10px 15px; 
            border-radius: 8px; 
            border: 1px solid var(--border-color);
            background-color: var(--card-bg-color);
            cursor: pointer;
            font-size: 15px;
            transition: all 0.2s ease;
        }
        #recordBtn.recording {
            color: var(--destructive-color);
            border-color: var(--destructive-color);
        }
        #recordBtn.saved {
            color: #34c759;
            border-color: #34c759;
        }

        /* Phrase List */
        #toggleManageBtn {
            background: none;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 15px;
            width: 100%;
            margin-top: 15px;
            font-size: 15px;
            cursor: pointer;
        }
        #manageSection.hidden {
            display: none;
        }
        #phraseList { list-style: none; padding: 0; margin-top: 15px; }
        .phrase-item {
            display: flex;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
        }
        .phrase-item:last-child { border-bottom: none; }
        .phrase-name { flex-grow: 1; text-align: left; font-size: 15px; }
        .phrase-controls button {
            padding: 5px 10px;
            margin-left: 5px;
            border-radius: 8px;
            border: 1px solid transparent;
            background-color: transparent;
            cursor: pointer;
        }

        #player { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Praise Loop</h1>
        <p>For Caroline, the goodest girl.</p>

        <div class="main-controls">
            <button id="loopBtn" class="start">Start Loop</button>
            <div class="status">
                <span id="statusIndicator" class="status-indicator"></span>
                <span id="statusText">Idle</span>
            </div>
        </div>

        <div class="settings">
            <div class="setting-item">
                <label for="min_pause">Min Pause (s)</label>
                <input type="number" id="min_pause" value="2" min="0">
            </div>
            <div class="setting-item">
                <label for="max_pause">Max Pause (s)</label>
                <input type="number" id="max_pause" value="10" min="0">
            </div>
        </div>

        <h2>Record New Praise</h2>
        <div class="recording-controls">
            <button id="recordBtn">Record</button>
            <span id="recordTimer">00:00</span>
        </div>
        <div class="settings" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
             <div class="setting-item">
                <label for="trimSilence">Auto-trim silence</label>
                <input type="checkbox" id="trimSilence" checked>
            </div>
        </div>

        <button id="toggleManageBtn">Manage Phrases</button>

        <div id="manageSection" class="hidden">
            <h2>Phrases</h2>
            <ul id="phraseList"></ul>
        </div>

    </div>

    <audio id="player"></audio>

    <script>
        // State
        let mediaRecorder;
        let audioChunks = [];
        let recordStartTime;
        let recordTimerInterval;
        let loopRunning = false;
        let praiseTimeout;
        let countdownInterval;

        // Elements
        const player = document.getElementById('player');
        const loopBtn = document.getElementById('loopBtn');
        const minPauseInput = document.getElementById('min_pause');
        const maxPauseInput = document.getElementById('max_pause');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const recordBtn = document.getElementById('recordBtn');
        const recordTimer = document.getElementById('recordTimer');
        const phraseList = document.getElementById('phraseList');
        const toggleManageBtn = document.getElementById('toggleManageBtn');
        const manageSection = document.getElementById('manageSection');
        const trimSilenceCheckbox = document.getElementById('trimSilence');


        // --- Phrase Management ---
        async function fetchPhrases() {
            const res = await fetch('/phrases');
            const phrases = await res.json();
            renderPhrases(phrases);
        }

        function renderPhrases(phrases) {
            phraseList.innerHTML = '';
            if (phrases.length === 0) {
                phraseList.innerHTML = '<p style="color: #6e6e73;">No phrases recorded yet.</p>';
                return;
            }
            phrases.forEach(filename => {
                const li = document.createElement('li');
                li.className = 'phrase-item';
                li.dataset.filename = filename;
                li.innerHTML = `
                    <span class="phrase-name">${filename}</span>
                    <div class="phrase-controls">
                        <button onclick="playPhrase('${filename}')">▶️</button>
                        <button onclick="renamePhrase('${filename}')">✏️</button>
                        <button onclick="deletePhrase('${filename}')">🗑️</button>
                    </div>
                `;
                phraseList.appendChild(li);
            });
        }

        async function playPhrase(filename) {
            player.src = `/praise/${filename}`;
            player.play();
        }

        async function deletePhrase(filename) {
            if (!confirm(`Are you sure you want to delete ${filename}?`)) return;

            await fetch('/delete_phrase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename })
            });
            fetchPhrases();
        }

        async function renamePhrase(oldFilename) {
            const newFilename = prompt("Enter the new filename:", oldFilename);

            if (!newFilename || newFilename === oldFilename) {
                return; // User cancelled or didn't change the name
            }

            // Ensure the filename ends with .wav
            const finalFilename = newFilename.endsWith('.wav') ? newFilename : newFilename + '.wav';

            const res = await fetch('/rename_phrase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_filename: oldFilename, new_filename: finalFilename })
            });

            if (res.ok) {
                fetchPhrases();
            } else {
                const error = await res.text();
                alert(`Error renaming file: ${error}`);
            }
        }

        // --- Recording ---
        recordBtn.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                stopRecording();
            } else {
                startRecording();
            }
        });

        async function startRecording() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            recordBtn.textContent = 'Stop';
            recordBtn.classList.remove('saved');
            recordBtn.classList.add('recording');
            audioChunks = [];
            recordStartTime = Date.now();
            recordTimerInterval = setInterval(() => {
                const seconds = Math.floor((Date.now() - recordStartTime) / 1000);
                recordTimer.textContent = new Date(seconds * 1000).toISOString().substr(14, 5);
            }, 1000);

            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
        }

        function stopRecording() {
            mediaRecorder.stop();
            clearInterval(recordTimerInterval);
            recordTimer.textContent = '00:00';
            recordBtn.textContent = 'Saving...';
            recordBtn.classList.remove('recording');
            
            mediaRecorder.addEventListener('stop', async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio_data', audioBlob);
                formData.append('trim_silence', trimSilenceCheckbox.checked);

                try {
                    const res = await fetch('/add_phrase', { method: 'POST', body: formData });
                    if (res.ok) {
                        recordBtn.textContent = 'Saved!';
                        recordBtn.classList.add('saved');
                        fetchPhrases();
                    } else {
                        recordBtn.textContent = 'Error!';
                    }
                } catch (error) {
                    console.error('Upload error:', error);
                    recordBtn.textContent = 'Error!';
                } finally {
                    setTimeout(() => {
                        recordBtn.textContent = 'Record';
                        recordBtn.classList.remove('saved');
                    }, 2000);
                }
            });
        }

        // --- UI ---
        toggleManageBtn.addEventListener('click', () => {
            manageSection.classList.toggle('hidden');
        });

        // --- Loop Control ---
        loopBtn.addEventListener('click', () => {
            loopRunning = !loopRunning;
            if (loopRunning) {
                startLoop();
            } else {
                stopLoop();
            }
        });

        function startLoop() {
            loopBtn.textContent = 'Stop Loop';
            loopBtn.className = 'stop';
            statusIndicator.classList.add('active');
            playRandomPhrase();
        }

        function stopLoop() {
            loopBtn.textContent = 'Start Loop';
            loopBtn.className = 'start';
            statusIndicator.classList.remove('active');
            statusText.textContent = 'Idle';
            player.pause();
            clearTimers();
        }

        function clearTimers() {
            clearTimeout(praiseTimeout);
            clearInterval(countdownInterval);
        }

        async function playRandomPhrase() {
            clearTimers();
            try {
                const res = await fetch('/random_praise');
                if (!res.ok) {
                    statusText.textContent = 'No phrases to play.';
                    stopLoop();
                    return;
                }
                const blob = await res.blob();
                player.src = URL.createObjectURL(blob);
                await player.play();
                statusText.textContent = 'Playing...';
            } catch (error) {
                console.error("Playback error:", error);
                statusText.textContent = 'Error. Check console.';
                stopLoop();
            }
        }

        function scheduleNextPlay() {
            if (!loopRunning) return;
            clearTimers();

            const minPause = parseFloat(minPauseInput.value) * 1000;
            const maxPause = parseFloat(maxPauseInput.value) * 1000;
            const delay = Math.random() * (maxPause - minPause) + minPause;
            const endTime = Date.now() + delay;

            function updateCountdown() {
                const remaining = endTime - Date.now();
                if (remaining <= 0) {
                    clearInterval(countdownInterval);
                    if(loopRunning) playRandomPhrase();
                    return;
                }
                statusText.textContent = `Next praise in ${Math.ceil(remaining / 1000)}s...`;
            }

            countdownInterval = setInterval(updateCountdown, 500);
            updateCountdown();
        }

        player.addEventListener('ended', scheduleNextPlay);

        // Initial Load
        document.addEventListener('DOMContentLoaded', fetchPhrases);

    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/phrases')
def list_phrases():
    return jsonify(get_phrases())

@app.route('/praise/<filename>')
def get_praise_file(filename):
    # Security: Ensure filename is safe
    if '..' in filename or filename.startswith('/'):
        return "Invalid filename", 400
    file_path = os.path.join(PHRASES_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, mimetype='audio/wav')

@app.route('/random_praise')
def random_praise():
    phrases = get_phrases()
    if not phrases:
        return "No phrases available", 404
    
    random_phrase = random.choice(phrases)
    file_path = os.path.join(PHRASES_DIR, random_phrase)
    return send_file(file_path, mimetype='audio/wav')

@app.route('/add_phrase', methods=['POST'])
def add_phrase():
    if 'audio_data' not in request.files:
        return "No audio data", 400
    
    audio_file = request.files['audio_data']
    trim_silence = request.form.get('trim_silence') == 'true'

    # Generate a unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"praise_{timestamp}.wav"
    filepath = os.path.join(PHRASES_DIR, filename)
    
    # Save the initial audio file
    audio_file.save(filepath)

    # If trimming is requested, process the file
    if trim_silence:
        sound = AudioSegment.from_file(filepath, format="wav")

        # Find non-silent chunks
        # Using a silence threshold of -16dB relative to the file's max dBFS
        # and a minimum silence length of 400ms
        nonsilent_chunks = detect_nonsilent(
            sound, 
            min_silence_len=400, 
            silence_thresh=sound.dBFS - 16
        )

        if nonsilent_chunks:
            # Get the start of the first non-silent chunk and the end of the last one
            start_trim = nonsilent_chunks[0][0]
            end_trim = nonsilent_chunks[-1][1]
            trimmed_sound = sound[start_trim:end_trim]
            
            # Overwrite the original file with the trimmed version
            trimmed_sound.export(filepath, format="wav")

    return jsonify({"success": True, "filename": filename})

@app.route('/delete_phrase', methods=['POST'])
def delete_phrase():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return "Filename not provided", 400

    # Security: Ensure filename is safe
    if '..' in filename or filename.startswith('/'):
        return "Invalid filename", 400

    file_path = os.path.join(PHRASES_DIR, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"success": True, "filename": filename})
    else:
        return "File not found", 404

@app.route('/rename_phrase', methods=['POST'])
def rename_phrase():
    data = request.get_json()
    old_filename = data.get('old_filename')
    new_filename = data.get('new_filename')

    if not old_filename or not new_filename:
        return "Old or new filename not provided", 400

    # Security: Sanitize and validate new filename
    if '..' in new_filename or '/' in new_filename or not new_filename.endswith('.wav'):
        return "Invalid new filename", 400
    
    old_path = os.path.join(PHRASES_DIR, old_filename)
    new_path = os.path.join(PHRASES_DIR, new_filename)

    if not os.path.exists(old_path):
        return "File to rename not found", 404
    
    if os.path.exists(new_path):
        return "A file with the new name already exists", 409 # Conflict

    os.rename(old_path, new_path)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5050)
