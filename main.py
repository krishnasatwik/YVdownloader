from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from yt_dlp import YoutubeDL

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("frontend.html")

@app.post("/download/")
async def download_video_endpoint(url: str = Form(...)):
    try:
        video_title = download_video(url)
        return JSONResponse(content={"message": f"Video '{video_title}' downloaded successfully"})
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download video: {e}")

import os
from yt_dlp import YoutubeDL

import os
import subprocess
from yt_dlp import YoutubeDL

def download_video(url, output_path='.'):
    # Create a temporary directory for video and audio files
    temp_dir = os.path.join(output_path, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # Options for yt-dlp

    def hook(d):
        if d['status'] == 'finished':
            print(f"Done downloading {d['filename']}")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Download the best video and audio streams
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),  # Save files to temp directory
        'noplaylist': True,
        'progress_hooks': [hook],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'video')

            video_file = os.path.join(temp_dir, f"{video_title}.mp4")
            audio_file = os.path.join(temp_dir, f"{video_title}.webm")
            final_file = os.path.join(output_path, f"{video_title}.mp4")

            if os.path.exists(video_file) and os.path.exists(audio_file):
                # Merge using FFmpeg
                command = [
                    'ffmpeg', 
                    '-i', video_file,    # Input video file
                    '-i', audio_file,    # Input audio file
                    '-c:v', 'copy',      # Copy the video codec (no re-encoding)
                    '-c:a', 'aac',       # Convert audio to AAC codec
                    '-strict', 'experimental',  # Required for some FFmpeg builds
                    final_file           # Output file
                ]

                # Execute FFmpeg command
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg error: {result.stderr}")

                # Clean up temporary files
                os.remove(video_file)
                os.remove(audio_file)
                print(f"Video saved as: {final_file}")

            else:
                print("Error: Video or audio file not found")

            return video_title

    except Exception as e:
        print(f"Error during video download: {e}")
        raise e


