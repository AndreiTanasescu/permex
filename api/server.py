from .match_perms import search_permission
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing_extensions import Annotated
from typing import Union
import uvicorn

app = FastAPI()

origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/site", StaticFiles(directory="frontend", html=True), name='frontend')

@app.get("/")
def serve_spa():
    return RedirectResponse("/site")


@app.get('/api/perm/search')
async def search_perm(perm: Annotated[Union[str, None], Query(max_length=256)]):
    perms = search_permission(perm)

    return perms


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
