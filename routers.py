from fastapi import UploadFile, File, APIRouter

router = APIRouter(prefix='/zip', tags=['upload'])


@router.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    with open("git_repositories/" + file.filename, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": file.filename, "message": "ZIP файл загружен"}
