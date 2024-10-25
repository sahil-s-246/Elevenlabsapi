import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

CHUNK_SIZE = 1024
url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv("ID")}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": os.getenv("API_KEY")
}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "audio_file": None})


@app.post("/api/media", response_class=FileResponse)
async def post_media_file(request: Request, name: str = Form(...)):
    """
    Receive name, generate audio file & return it

    """
    data = {
        "text": f"My name is {name}",
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error generating audio")

    # Write file to disk
    audio_filename = f'tmp/{name}.mp3'
    with open(audio_filename, 'wb') as f:
        f.write(response.content)
    return FileResponse(f"tmp/{name}.mp3", media_type='application/octet-stream', filename=f"{name}.mp3")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
