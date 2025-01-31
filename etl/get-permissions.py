from decouple import config

import sys
import requests
import json
import re

tenant = config('tenant', default=False)
subscriptionId = config('subscriptionId')

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

token = get_new_token()

def write_file_content(output_filename, c):
    with open(output_filename, 'w') as f:
        f.write(c)


def refresh_builtin_roles(test_api_url):
    global token

    api_call_headers = {'Authorization': 'Bearer ' + token}
    api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)

    if  api_call_response.status_code == 401:
        token = get_new_token()
        api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)
        # poor man's retry ?
    else:
        return api_call_response.text


def refresh_all_roles_definitions():
    """not called, but useful."""
    test_api_url='https://management.azure.com/providers/Microsoft.Authorization/roleDefinitions?api-version=2022-04-01'
    output_filename = 'role-definitions.json'
    
    call_result = refresh_builtin_roles(test_api_url)
    
    write_file_content(output_filename, call_result)


def download_provider_definitions(provider_name, api_version):
    test_api_url = f"https://management.azure.com/providers/{provider_name}/operations?api-version={api_version}"
    
    call_result = refresh_builtin_roles(test_api_url)
    return call_result
    


def refresh_provider_permissions(provider_name, api_version):
    """return the latest API version for the provider, if api_version is invalid"""
    call_result = download_provider_definitions(provider_name, api_version)

    if len(call_result) < 5000 and 'The supported api-versions are' in call_result:
        all_dates = re.findall(r'(\d{4}-\d{2}-\d{2}(?:-preview)?)', call_result)
        max_date = sorted(all_dates)[-2]
        api_version = max_date

        call_result = download_provider_definitions(provider_name, api_version)

        # retry : get latest api version.

    output_filename = f'role-definitions-{provider_name}-{api_version}.json'
    write_file_content(output_filename, call_result)

    print(f'Finished refreshing {output_filename}')


refresh_provider_permissions(provider_name='Microsoft.Authorization',
    api_version='2019-05-01')


def redownload_all_providers():
    import sys
    sys.path.append('../')
    
    from api.match_perms import PermissionMatcher
    
    m = PermissionMatcher('../data/all-role-definitions.json')

    print( sorted(m.provider_tree.providerDict.keys()) )

    for provider in sorted(m.provider_tree.providerDict.keys()):
        if len(provider) < 3:
            continue

        refresh_provider_permissions(provider_name=provider, api_version='2050-01-01')

redownload_all_providers()
