from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static folder (for future CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
async def serve_index():
    # index.html in root
    return FileResponse("index.html")


@app.post("/tts")
async def tts(
    text: str = Form(...),
    lang: str = Form("English"),
    voice: str = Form(""),
    rate: str = Form("0%"),
):
    # Fallback voices per language
    default_voices = {
        "English": "en-US-AriaNeural",
        "Tamil": "ta-IN-PallaviNeural",
        "Hindi": "hi-IN-MadhurNeural",
        "Malayalam": "ml-IN-MidhunNeural",
    }

    if not voice:
        voice = default_voices.get(lang, "en-US-AriaNeural")

    # Ensure rate like "+0%" or "-20%"
    if not rate.endswith("%"):
        rate = f"{int(rate):+d}%"

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)

    mp3_bytes = io.BytesIO()
    await communicate.stream(mp3_bytes)  # stream to buffer
    mp3_bytes.seek(0)

    return StreamingResponse(
        mp3_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=podcast.mp3"},
    )
