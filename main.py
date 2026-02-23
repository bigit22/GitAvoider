import uvicorn
from fastapi import FastAPI

from routers import router as zip_router

app = FastAPI()

app.include_router(zip_router)


def main():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == '__main__':
    main()
