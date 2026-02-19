from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import edge_tts
import asyncio
import io

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/tts")
async def tts(text: str = Form(...), voice: str = Form("en-US-AriaNeural"), rate: str = Form("0%")):
    communicate = edge_tts.Communicate(text, voice, rate)
    mp3_bytes = io.BytesIO()
    await communicate.stream_to_file(mp3_bytes)
    mp3_bytes.seek(0)
    return StreamingResponse(mp3_bytes, media_type="audio/mpeg")

# Serve frontend
@app.get("/")
async def root():
    return {"message": "TTS API ready"}
