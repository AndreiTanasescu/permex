import sys
sys.path.append('./')

from api.match_perms import filter_matching, PermissionMatcher

def test_positive_match():
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

    #print(actual)
    assert actual == expected


