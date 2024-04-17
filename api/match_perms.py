from typing import List

##
## Should remove not actions
## Should interpret data actions
## transform to more efficient data structure
## integrate data reload for github.
## Doesn't remove wildcard notactions
## return the number of data comparisons. How to reduce ?
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
