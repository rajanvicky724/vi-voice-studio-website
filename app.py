from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import asyncio
import io
from pathlib import Path

app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def serve_index():
    return FileResponse("index.html")  # Serve from ROOT

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")  # Optional

@app.post("/tts")
async def tts(text: str = Form(...), voice: str = Form("en-US-AriaNeural"), rate: str = Form("0%"), lang: str = Form("English")):
    voices = {
        "English": "en-US-AriaNeural", "Tamil": "ta-IN-PallaviNeural",
        "Hindi": "hi-IN-MadhurNeural", "Malayalam": "ml-IN-MidhunNeural"
    }
    voice = voices.get(lang, voice)
    
    communicate = edge_tts.Communicate(text, voice, rate)
    mp3_bytes = io.BytesIO()
    await communicate.stream_to_file(mp3_bytes)
    mp3_bytes.seek(0)
    return StreamingResponse(
        mp3_bytes, 
        media_type="audio/mpeg", 
        headers={"Content-Disposition": "attachment; filename=podcast.mp3"}
    )
