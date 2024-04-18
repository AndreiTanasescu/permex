from typing import List
import json

##
## Should interpret data actions
## return the number of data comparisons. How to reduce ? Inverted tree ?
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

            for action in all_actions:
                provider = action.split('/')[0]

                if not provider in self.providerDict:
                    self.providerDict[provider] = []
                
                role_already_added = False
                for existing_role in self.providerDict[provider]:
                    if existing_role['properties']['roleName'] == role_name:
                        role_already_added = True
                        continue
                
                if not role_already_added:
                    self.providerDict[provider].append(role)

    def get_provider_roles(self, provider):
        return self.providerDict[provider]


with open('./data/all-role-definitions.json', mode='r', encoding='utf-8') as f:
    j = json.load(f)
    all_loaded_roles = j['value']
    provider_tree = ProviderInvertedTree(all_loaded_roles)

print(f'Loaded {len(all_loaded_roles)} roles')


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


def search_permission(perm: str):
    all_matching_actions = []

    for role in provider_tree.get_provider_roles(perm.split('/')[0]):
        if 'properties' not in role:
            continue

        permissions = role['properties']['permissions'][0]

        all_actions = permissions['actions']
      
        matching_actions = filter_matching(perm, all_actions)

        all_notactions = permissions['notActions']

        matching_notactions = filter_matching(perm, all_notactions)
        if len(matching_notactions) > 0:
            continue # as this is a notAction.

        if len(matching_actions) > 0:
            all_matching_actions.append(
                f"{role['properties']['roleName']} ==> permission: {matching_actions}")

    return all_matching_actions

