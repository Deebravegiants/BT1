# [M] The removeAllowedRouter() Functionality Is Broken

## Summary
Severity: Medium
Contest weight: 0.3753
Dataset id: 15618
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The removeAllowedRouter() function implements a check if the passed _router is included in _allAllowedRouters, but if it is included the function reverts with Enigma__RouterWhitelisted. In the other case when it does not exist the _remove() function from EnumerableSet.sol will return false and therefore the router can not be removed.

## Recommendation
Fix the check in the following way:
```solidity
// @notice removes a allowed router for rebalancing swaps
function removeAllowedRouter(address _router) external onlyOwner {
    if (!_allAllowedRouters.contains(_router)) revert Enigma__RouterWhitelisted(_router);
    _allAllowedRouters.remove(_router);
    emit RouterAllowed(_router, false);
}
```
