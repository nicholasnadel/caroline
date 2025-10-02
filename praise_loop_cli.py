#!/usr/bin/env python3

"""
CLI Praise Loop for Caroline
A simple, reliable command-line version that plays random praise clips at random intervals.
"""

import argparse
import os
import random
import time
import subprocess
import sys
from pathlib import Path
import threading

def is_valid_audio_file(file_path):
    """Test if an audio file is valid without playing it."""
    try:
        if sys.platform == "darwin":  # macOS
            # Use afinfo to check file validity without playing
            result = subprocess.run(
                ["afinfo", str(file_path)], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        elif sys.platform.startswith("linux"):  # Linux
            # Use file command to check if it's a valid audio file
            result = subprocess.run(
                ["file", "--mime-type", str(file_path)], 
                capture_output=True, 
                timeout=5
            )
            if result.returncode == 0:
                output = result.stdout.decode().lower()
                return "audio/" in output
        # For other platforms, assume valid
        return True
    except Exception:
        return False

def get_audio_files(directory):
    """Get all valid .wav files from the phrases directory."""
    phrases_dir = Path(directory)
    if not phrases_dir.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)
    
    all_files = list(phrases_dir.glob("*.wav"))
    if not all_files:
        print(f"Error: No .wav files found in '{directory}'.")
        sys.exit(1)
    
    # Filter out corrupted files
    valid_files = []
    corrupted_files = []
    
    print("🔍 Checking audio files...")
    for file in all_files:
        if is_valid_audio_file(file):
            valid_files.append(file)
        else:
            corrupted_files.append(file)
    
    if corrupted_files:
        print(f"⚠️  Skipping {len(corrupted_files)} corrupted files:")
        for file in corrupted_files:
            print(f"   ❌ {file.name}")
    
    if not valid_files:
        print("Error: No valid audio files found.")
        sys.exit(1)
    
    return valid_files

def play_audio_file(file_path):
    """Play an audio file using the system's default audio player."""
    try:
        # Try different audio players based on the platform
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", str(file_path)], check=True)
        elif sys.platform.startswith("linux"):  # Linux
            # Try common Linux audio players
            players = ["paplay", "aplay", "play"]
            for player in players:
                try:
                    subprocess.run([player, str(file_path)], check=True, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            raise Exception("No suitable audio player found")
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.PlaySound(str(file_path), winsound.SND_FILENAME)
        else:
            print(f"Unsupported platform: {sys.platform}")
            sys.exit(1)
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False
    return True

def start_caffeinate():
    """Start caffeinate process to prevent system sleep on macOS."""
    if sys.platform == "darwin":
        try:
            # Use caffeinate to prevent idle sleep
            process = subprocess.Popen(
                ["caffeinate", "-i"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return process
        except FileNotFoundError:
            print("⚠️  caffeinate not found, falling back to basic daemon")
            return None
    return None

def keep_awake_daemon():
    """Background thread to prevent system sleep by periodically running a harmless command."""
    while True:
        try:
            # Run a harmless command every 4 minutes to prevent sleep
            subprocess.run(["date"], capture_output=True, timeout=5)
        except Exception:
            pass
        time.sleep(240)  # 4 minutes

def main():
    parser = argparse.ArgumentParser(
        description="Play random praise clips for Caroline at random intervals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use defaults: 2-4 second intervals, phrases/ directory
  %(prog)s --min 5 --max 15   # 5-15 second intervals
  %(prog)s --dir ./sounds     # Use ./sounds directory instead of phrases/
  %(prog)s --use-daemon       # Use daemon thread instead of caffeinate on macOS
  %(prog)s --min 1 --max 3 --dir custom_phrases/
        """
    )
    
    parser.add_argument(
        "--min", 
        type=float, 
        default=2.0,
        help="Minimum pause between praise clips in seconds (default: 2.0)"
    )
    
    parser.add_argument(
        "--max", 
        type=float, 
        default=4.0,
        help="Maximum pause between praise clips in seconds (default: 4.0)"
    )
    
    parser.add_argument(
        "--dir", 
        default="phrases",
        help="Directory containing .wav files (default: phrases)"
    )
    
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List available audio files and exit"
    )
    
    parser.add_argument(
        "--no-keep-awake", 
        action="store_true",
        help="Disable built-in keep-awake daemon (computer may sleep)"
    )
    
    parser.add_argument(
        "--use-daemon", 
        action="store_true",
        help="Use daemon thread instead of caffeinate on macOS"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.min < 0:
        print("Error: Minimum pause cannot be negative.")
        sys.exit(1)
    
    if args.max < args.min:
        print("Error: Maximum pause must be greater than or equal to minimum pause.")
        sys.exit(1)
    
    # Get audio files
    audio_files = get_audio_files(args.dir)
    
    if args.list:
        print(f"Found {len(audio_files)} audio files in '{args.dir}':")
        for file in sorted(audio_files):
            print(f"  {file.name}")
        sys.exit(0)
    
    print(f"🐕 Caroline Praise Loop CLI")
    print(f"📁 Directory: {args.dir}")
    print(f"🎵 Found {len(audio_files)} audio files")
    print(f"⏱️  Intervals: {args.min}-{args.max} seconds")
    
    # Start keep-awake mechanism unless disabled
    caffeinate_process = None
    if not args.no_keep_awake:
        if sys.platform == "darwin" and not args.use_daemon:
            # Use caffeinate on macOS by default for better reliability
            caffeinate_process = start_caffeinate()
            if caffeinate_process:
                print(f"💤 Keep-awake: caffeinate enabled")
            else:
                # Fallback to daemon if caffeinate fails
                daemon_thread = threading.Thread(target=keep_awake_daemon, daemon=True)
                daemon_thread.start()
                print(f"💤 Keep-awake: daemon enabled (caffeinate fallback)")
        else:
            # Use daemon thread (non-macOS or --use-daemon flag)
            daemon_thread = threading.Thread(target=keep_awake_daemon, daemon=True)
            daemon_thread.start()
            print(f"💤 Keep-awake: daemon enabled")
    else:
        print(f"💤 Keep-awake: disabled")
    
    print(f"🎯 Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Pick a random audio file
            chosen_file = random.choice(audio_files)
            
            print(f"🎵 Playing: {chosen_file.name}")
            
            # Play the audio file
            if not play_audio_file(chosen_file):
                print("⚠️  Audio playback failed, continuing...")
            
            # Calculate random pause
            pause_duration = random.uniform(args.min, args.max)
            
            print(f"⏳ Next praise in {pause_duration:.1f} seconds...")
            time.sleep(pause_duration)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Caroline is still the goodest girl!")
        # Clean up caffeinate process if it was started
        if caffeinate_process:
            try:
                caffeinate_process.terminate()
                caffeinate_process.wait(timeout=2)
            except Exception:
                pass
        sys.exit(0)

if __name__ == "__main__":
    main()