
"""
Microsoft.Compute/availabilitySets/*

Microsoft.Compute/availabilitySets/vmSizes/read
Microsoft.Compute/availabilitySets/delete
Microsoft.Compute/AvailabilitySets/write
Microsoft.Compute/AvailabilitySets/bla/action

Microsoft.Compute2/AvailabilitySets/write
"""
from typing import List

def filter_matching(target:str, candidates:List[str]) -> List[str]:
    """does not change the order"""
    if target == '*':
        return candidates

    target = target.lower()

    matches = []
    for i in candidates:
        # considering so far there is only one * per candidate
        # and that resource names are typically not repeated in 
        # later parts of the strings, this is ok.
        if all([ r in target for r in i.lower().split('*')]):
            matches.append(i)
        
    return matches



expected = [
    'Microsoft.Compute/availabilitySets/*'
]

actual = filter_matching('Microsoft.Compute/availabilitySets/delete', 
    [
        'Microsoft.Compute/availabilitySets/vmSizes/read',
        'Microsoft.Compute/availabilitySets/*',
        'Microsoft.Compute/AvailabilitySets/write',
        'Microsoft.Compute/AvailabilitySets/bla/action'
    ]
)

print(actual)
assert actual == expected

import json

with open('./data/all-role-definitions.json') as f:
    j = json.load(f)
    all_roles = j['value']


print(f'Loaded {len(all_roles)} roles')



from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.responses import FileResponse

#from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
#from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
#from fastapi_proxiedheadersmiddleware import ProxiedHeadersMiddleware

from fastapi.middleware.cors import CORSMiddleware

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
    # t = "Microsoft.Storage/storageAccounts/listKeys/action"
    # t = 'Microsoft.Storage/storageAccounts/regeneratekey/action'
    # t = 'Microsoft.Automation/automationAccounts/runbooks/read'
    # Microsoft.MachineLearningServices/workspaces/resynckeys/action

    print(perm)

    all_matching_permissions = []
    for role in all_roles:
        if 'properties' not in role:
            continue

        role_perms = role['properties']['permissions'][0]['actions']

        matching_permissions = filter_matching(perm, role_perms)

        if len(matching_permissions) > 0:
            all_matching_permissions.append(f"{role['properties']['roleName']} ==> permission: {matching_permissions}")
            
            print(json.dumps(role, indent=2))
            #print(role)
            print('==========')
            print(matching_permissions)
            print('==========')
            print('\n----------\n')


    return all_matching_permissions


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")