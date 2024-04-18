

from decouple import config

import sys
import requests
import json

tenant = config('tenant', default=False)
subscriptionId = config('subscriptionId')

_secret_id = config('_secret_id')
client_id = config('client_id')
client_secret = config('client_secret')



def get_new_token(): # 
    """Obtain a new token for the management API"""
    auth_server_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    
    token_req_payload = {
        'grant_type': 'client_credentials', 
        'scope': 'https://management.core.windows.net/.default',
        'client_id': client_id,
        'client_secret': client_secret
    }

    token_response = requests.post(auth_server_url,
        data=token_req_payload, verify=False, allow_redirects=False, timeout=10)
             
    if token_response.status_code != 200:
        print("Failed to obtain token from the OAuth 2.0 server. \r\nCode " +
            f"{token_response.content.decode('utf-8')}. \r\nURL: {auth_server_url}", file=sys.stderr)
        print(token_response)
        sys.exit(1)

    print("Successfuly obtained a new token")
    tokens = json.loads(token_response.text)
    
    return tokens['access_token']


def refresh_builtin_roles(test_api_url, output_filename):
    token = get_new_token()

    api_call_headers = {'Authorization': 'Bearer ' + token}
    api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)

    if  api_call_response.status_code == 401:
        token = get_new_token()
    else:
        with open(output_filename, 'w') as f:
            f.write(api_call_response.text)

def refresh_all_roles_definitions():
    test_api_url='https://management.azure.com/providers/Microsoft.Authorization/roleDefinitions?api-version=2022-04-01'
    output_filename = 'role-definitions.json'
    refresh_builtin_roles(test_api_url, output_filename)


def refresh_provider_permissions(provider_name, api_version):
    test_api_url = f"https://management.azure.com/providers/{provider_name}/operations?api-version={api_version}"
    output_filename = f'role-definitions-{provider_name}-{api_version}.json'
    refresh_builtin_roles(test_api_url, output_filename)

    print(f'Finished refreshing {output_filename}')

refresh_provider_permissions(provider_name='Microsoft.Authorization',
    api_version='2017-05-01')

# refresh_provider_permissions(provider_name='Microsoft.MachineLearningServices', 
#     api_version='2024-01-01-preview')

# refresh_provider_permissions(provider_name='Microsoft.Compute', 
#     api_version='2024-03-01')
    
refresh_all_roles_definitions()