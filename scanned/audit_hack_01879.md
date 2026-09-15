# [M] Missing Validation Checks in `execute`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The `Pool` contract implements a threshold voting mechanism for some changes in the contract state, where either the pool manager or a committee member can propose a change by calling `claim`, `changePoolManager`, `addToCommittee`, `removeFromCommittee`, or `changeCommitteeThreshold`, and then the committee has a time period for voting. If the threshold is reached during this period, then anyone can call `execute` to execute the state change.

While some validation checks are implemented in the proposal phase, this is not enough to ensure that business logic rules around these changes are completely enforced.

1. `_executeRemoveFromCommittee` – While the `removeFromCommittee` function makes sure that `committeeArray.length > committeeThreshold`, i.e., that there should always be enough committee members to reach the threshold, the same validation check is not enforced in `_executeRemoveFromCommittee`. To better illustrate the issue, let's consider the following example: `committeeArray.length = 5`, `committeeThreshold = 4`, and now `removeFromCommittee` is called two times in a row, where the second call is made before the first call reaches the threshold. In this case, both requests will be executed successfully, and we end up with `committeeArray.length = 3` and `committeeThreshold = 4`, which is clearly not desired.
 
2. `_executeChangeCommitteeThreshold` – Applying the same concept here, this function lacks the validation check of `threshold_ <= committeeArray.length`, leading to the same issue as above. Let's consider the following example: `committeeArray.length = 3`, `committeeThreshold = 2`, and now `changeCommitteeThreshold`is called with `threshold_ = 3`, but before this request is executed, `removeFromCommittee` is called. After both requests have been executed successfully, we will end up with `committeeThreshold = 3` and `committeeArray.length = 2`, which is clearly not desired.

#### Examples


**contracts/Pool.sol:L783**
```solidity
function _executeRemoveFromCommittee(address who_) private {
```


**contracts/Pool.sol:L796**
```solidity
function _executeChangeCommitteeThreshold(uint256 threshold_) private {
```

#### Recommendation

Apply the same validation checks in the functions that execute the state change.
