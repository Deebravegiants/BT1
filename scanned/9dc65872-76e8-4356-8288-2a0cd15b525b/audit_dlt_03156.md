# [M] Missing call to removeUserFromOrderbook after user is foreclosed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/113
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Orderbook’s removeUserFromOrderbook is used to delete/remove user’s bids when they are deemed foreclosed. This is called in Market newRental() and Treasury withdrawDeposit when users are determined to be foreclosed given their deposit and bid situation.

However, there is a missing call to removeUserFromOrderbook after user is marked foreclosed in collectRentUser. This will allow user's bids to remain in the order book and unless this removal is triggered by someone else, their bids will continue to stay and will affect future ownership calculations.

## Proof of Concept

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCTreasury.sol#L736-L737

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCOrderbook.sol#L572-L629

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCMarket.sol#L687-L690

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCTreasury.sol#L356-L366


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add call to removeUserFromOrderbook after user is marked foreclosed in collectRentUser()
