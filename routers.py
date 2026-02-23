import os
import shutil
import subprocess
import tempfile
import uuid

from fastapi import UploadFile, File, APIRouter, HTTPException

router = APIRouter(prefix="/upload")

TMP_ROOT = "./tmp"
os.makedirs(TMP_ROOT, exist_ok=True)

def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True)


@router.post("/upload-zip/{branch}")
async def upload_zip(branch: str = 'main', file: UploadFile = File(...)):
    fn = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join(TMP_ROOT, fn)
    with open(zip_path, "wb") as f:
        f.write(await file.read())

    extract_dir = tempfile.mkdtemp(dir=TMP_ROOT)

    try:
        # unpack
        shutil.unpack_archive(zip_path, extract_dir, "zip")

        # Ищем корень репозитория
        if os.path.isdir(os.path.join(extract_dir, ".git")):
            repo_dir = extract_dir
        else:
            subs = [d for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d))]
            if len(subs) == 1 and os.path.isdir(os.path.join(extract_dir, subs[0], ".git")):
                repo_dir = os.path.join(extract_dir, subs[0])
            else:
                raise HTTPException(400, "Не найден корень git-репозитория в ZIP")

        # git add/commit (если есть изменения)
        run(["git", "add", "-A"], cwd=repo_dir)
        st = subprocess.run(
            ["git", "diff-index", "--quiet", "HEAD"], cwd=repo_dir
        )
        if st.returncode != 0:
            run(["git", "commit", "-m", "Auto-update from ZIP"], cwd=repo_dir)

        # git push origin/<branch>
        run(["git", "push", "origin", branch], cwd=repo_dir)

        return {"status": "pushed", "branch": branch}

    finally:
        try:
            os.remove(zip_path)
            shutil.rmtree(extract_dir)
        except Exception as error:
            with open('logs.txt', 'a') as f:
                f.writelines(str(error))
