from typing import List

##
## Should interpret data actions
## return the number of data comparisons. How to reduce ? Inverted tree ?
## [x] integrate data reload for github. (Secrets)
## [x] Should remove not actions
##

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


def search_permission(perm: str, all_roles):
    all_matching_actions = []

    for role in all_roles:
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