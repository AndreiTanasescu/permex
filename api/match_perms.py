from typing import List
import json

##
## [x] Should interpret data actions
## return the number of data comparisons. How to reduce ? Inverted tree ?
## return a link to the role definition / number of permissions it gives.
## [x] integrate data reload for github. (Secrets)
## [x] Should remove not actions
## Owner, contibutor are now ... dissapeared
## Microsoft.Resources/subscriptions/resourceGroups/read is a good test for long lists.
##

class ProviderInvertedTree:
    providerDict = dict()

    def __init__(self, all_roles) -> None:
        for role in all_roles:
            role_name = role['properties']['roleName']
            
            if 'properties' not in role:
                continue

            permissions = role['properties']['permissions'][0]

            all_actions = permissions['actions']
            all_data_actions = permissions['dataActions']


            for action in all_actions + all_data_actions:
                provider = action.split('/')[0].strip().lower()

                if not provider in self.providerDict:
                    self.providerDict[provider] = []
                    # print(f'new provider {provider}')
                
                role_already_added = False
                for existing_role in self.providerDict[provider]:
                    if existing_role['properties']['roleName'] == role_name:
                        role_already_added = True
                        continue
                
                if not role_already_added:
                    self.providerDict[provider].append(role)
                    

    def contains_provider(self, provider):
        return provider.lower() in self.providerDict

    def get_provider_roles(self, provider):
        return self.providerDict[provider.lower()]


class PermissionMatcher:
    def __init__(self) -> None:
        with open('./data/all-role-definitions.json', mode='r', encoding='utf-8') as f:
            j = json.load(f)
            all_loaded_roles = j['value']
            self.provider_tree = ProviderInvertedTree(all_loaded_roles)

        print(f'Loaded {len(all_loaded_roles)} roles')

    def search_permission(self, perm: str):
        all_matching_actions = []
        requested_provider = perm.split('/')[0]

        if not self.provider_tree.contains_provider(requested_provider):
            return all_matching_actions

        for role in self.provider_tree.get_provider_roles(requested_provider):
            if 'properties' not in role:
                continue

            if 'permissions' not in role['properties']:
                continue

            permissions = role['properties']['permissions'][0]

            # skip if explicit deny
            all_notactions = permissions['notActions'] + permissions['notDataActions']

            matching_notactions = filter_matching(perm, all_notactions)
            if len(matching_notactions) > 0:
                continue # as this is a notAction.

            all_actions = permissions['actions'] + permissions['dataActions']
        
            matching_actions = filter_matching(perm, all_actions)

            if len(matching_actions) > 0:
                all_matching_actions.append(
                    f"{role['properties']['roleName']} ==> permission: {matching_actions}")

        return all_matching_actions


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
