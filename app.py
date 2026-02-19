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
    rate: str = Form("0"),   # raw number from frontend
):
    from pathlib import Path
    import uuid, os

    default_voices = {
        "English": "en-US-AriaNeural",
        "Tamil": "ta-IN-PallaviNeural",
        "Hindi": "hi-IN-MadhurNeural",
        "Malayalam": "ml-IN-MidhunNeural",
    }

    if not voice:
        voice = default_voices.get(lang, "en-US-AriaNeural")

    # ---- NORMALISE RATE: "0" -> "+0%", "10" -> "+10%", "-20" -> "-20%" ----
    try:
        rate_num = int(str(rate).replace("%", "").strip())
    except ValueError:
        rate_num = 0
    rate = f"{rate_num:+d}%"
    # -----------------------------------------------------------------------

    # temp file
    temp_dir = Path("tmp")
    temp_dir.mkdir(exist_ok=True)
    file_id = uuid.uuid4().hex
    out_path = temp_dir / f"{file_id}.mp3"

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(out_path))

    def iterfile():
        with open(out_path, "rb") as f:
            data = f.read()
        try:
            os.remove(out_path)
        except OSError:
            pass
        yield data

    return StreamingResponse(
        iterfile(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="podcast.mp3"'},
    )


