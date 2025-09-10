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

def is_valid_audio_file(file_path):
    """Test if an audio file can be played."""
    try:
        if sys.platform == "darwin":  # macOS
            result = subprocess.run(
                ["afplay", str(file_path)], 
                capture_output=True, 
                timeout=1  # Quick test
            )
            return result.returncode == 0
        # For other platforms, assume valid for now
        return True
    except (subprocess.TimeoutExpired, Exception):
        # If it times out, it's probably playing (valid)
        return True

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

def main():
    parser = argparse.ArgumentParser(
        description="Play random praise clips for Caroline at random intervals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use defaults: 2-10 second intervals, phrases/ directory
  %(prog)s --min 5 --max 15   # 5-15 second intervals
  %(prog)s --dir ./sounds     # Use ./sounds directory instead of phrases/
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
        default=10.0,
        help="Maximum pause between praise clips in seconds (default: 10.0)"
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
        sys.exit(0)

if __name__ == "__main__":
    main()