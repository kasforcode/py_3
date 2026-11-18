from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

UPLOADS_DIR = Path("uploads")
THUMBNAILS_DIR = UPLOADS_DIR / "thumbnails"
UPLOADS_DIR.mkdir(exist_ok=True)
THUMBNAILS_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in {"image/png", "image/jpeg"}:
        raise HTTPException(status_code=400, detail="Допустимы только PNG и JPEG")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Размер файла не должен превышать 5 МБ")

    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image = Image.open(BytesIO(content))
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(status_code=400, detail="Файл не является изображением") from error

    extension = ".png" if file.content_type == "image/png" else ".jpg"
    filename = f"{uuid4().hex}{extension}"
    image_path = UPLOADS_DIR / filename
    image.save(image_path)

    thumbnail = image.copy()
    thumbnail.thumbnail((200, 200))
    thumbnail_filename = f"thumbnail_{filename}"
    thumbnail_path = THUMBNAILS_DIR / thumbnail_filename
    thumbnail.save(thumbnail_path)

    return {
        "url": f"http://localhost:8000/uploads/{filename}",
        "thumbnail_url": f"http://localhost:8000/uploads/thumbnails/{thumbnail_filename}",
    }
