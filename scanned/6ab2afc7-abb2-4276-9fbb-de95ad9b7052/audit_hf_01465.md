# [M] Not capped array can grow too big and lead to out of gas error

## Summary
Severity: Medium
Contest weight: 0.4117
Dataset id: 7654
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _getCurrentSupply and includeInReward functions both loop over the _excluded array to find out if there are any excluded accounts. The problem is that the array is not capped and can push unlimited number of accounts to the array. If an account needs to be removed, a loop over the whole array is needed inside includeInReward to pop the account:
```solidity
require(_isExcluded[account], "Account is already excluded");
for (uint256 i = 0; i < _excluded.length; i++) {
    // @audit - this can run out of gas if _excluded array is too big
    if (_excluded[i] == account) {
        _excluded[i] = _excluded[_excluded.length - 1];
        _tOwned[account] = 0;
        _isExcluded[account] = false;
        _excluded.pop();
        break;
    }
}
```
If at some point there are a lot of excluded accounts in the array, iterating over them will be very costly and can result in a gas cost that is over the block gas limit. This will leave the contract in a state of DoS because the _getCurrentSupply is called in most of the core functions.

## Recommendation
Limit the number of accounts that can be excluded. Also, consider to cache the array length outside of the for loop to make the call more gas efficient.
