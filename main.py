from contextlib import asynccontextmanager

from controllers import post, auth
from database import database, metadata, engine
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.post import posts #noqa
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(post.router)
app.include_router(auth.router)