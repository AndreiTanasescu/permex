from .match_perms import filter_matching
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import json
import uvicorn

app = FastAPI()

origins = [
    "*",
]


with open('./data/all-role-definitions.json', mode='r', encoding='utf-8') as f:
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


app.mount("/site", StaticFiles(directory="frontend", html=True), name='frontend')

@app.get("/")
def serve_spa():
    return RedirectResponse("/site")


@app.get('/api/perm/search')
async def search_perm(perm: str):
    all_matching_actions = []

    for role in all_roles:
        if 'properties' not in role:
            continue

        all_actions = role['properties']['permissions'][0]['actions']
    
        matching_actions = filter_matching(perm, all_actions)

        all_notactions = role['properties']['permissions'][0]['notActions']

        matching_notactions = filter_matching(perm, all_notactions)
        if len(matching_notactions) > 0:
            continue # as this is a notAction.

        if len(matching_actions) > 0:
            all_matching_actions.append(
                f"{role['properties']['roleName']} ==> permission: {matching_actions}")
  
    return all_matching_actions


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
