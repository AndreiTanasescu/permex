from .match_perms import filter_matching
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import json
import uvicorn

app = FastAPI()

origins = [
    "*",
]


with open('./data/all-role-definitions.json') as f:
    j = json.load(f)
    all_roles = j['value']

print(f'Loaded {len(all_roles)} roles')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.add_middleware(ProxiedHeadersMiddleware)
#app.add_middleware(ProxyHeadersMiddleware)
#app.add_middleware(HTTPSRedirectMiddleware)

#app.mount("/site", StaticFiles(directory="frontend", html=True), name='frontend')

@app.get("/")
def serve_spa():
    return FileResponse("./frontend/index.html")

@app.get("/logo.jpg")
def serve_spa():
    return FileResponse("./frontend/logo.jpg")

@app.get("/api/heartbeat")
async def api_help():
    return {"message": f"Welcome."}


@app.get('/api/perm/search')
async def search_perm(perm: str):

    all_matching_permissions = []
    for role in all_roles:
        if 'properties' not in role:
            continue

        role_perms = role['properties']['permissions'][0]['actions']

        matching_permissions = filter_matching(perm, role_perms)

        if len(matching_permissions) > 0:
            all_matching_permissions.append(f"{role['properties']['roleName']} ==> permission: {matching_permissions}")
            
    return all_matching_permissions


if __name__ == "__main__":
    

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")