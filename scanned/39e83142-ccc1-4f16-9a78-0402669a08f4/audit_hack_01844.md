# [M] `_endingDelegations` list is redundant

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

`_endingDelegations` is a list of delegations that is created for optimisation purposes. 
But the only place it's used is in `getPurchasedAmount` function, so only a subset of all delegations is going to be updated.


**code/contracts/delegation/TokenState.sol:L159-L164**
```solidity
function getPurchasedAmount(address holder) public returns (uint amount) {
    // check if any delegation was ended
    for (uint i = 0; i < _endingDelegations[holder].length; ++i) {
        getState(_endingDelegations[holder][i]);
    }
    return _purchased[holder];
```

But `getPurchasedAmount` function is mostly used after iterating over all delegations of the holder.

#### Recommendation

Remove `_endingDelegations` and switch to a mechanism that does not require looping through delegations list of potentially unlimited size.
