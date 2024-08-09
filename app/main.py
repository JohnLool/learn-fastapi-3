from contextlib import asynccontextmanager

from fastapi import FastAPI
from routes import auth, notes
from database import init_db, delete_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_db()
    print("База очищена")
    await init_db()
    print("База создана")
    yield
    print("Выключение")

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
