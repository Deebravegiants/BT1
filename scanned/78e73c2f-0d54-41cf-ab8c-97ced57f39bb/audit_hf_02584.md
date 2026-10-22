# [H] Unsafe cast from int256 to uint256 in NativeVault._updateBalance() will overflow

## Summary
Severity: High
Contest weight: 0.7334
Dataset id: 13955
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In NativeVault._updateBalance(), assets is cast from int256 to uint256 directly as such:
```solidity
function _updateBalance(address _of, int256 assets) internal {
if (assets > 0) {
_increaseBalance(_of, uint256(assets));
} else if (assets < 0) {
_decreaseBalance(_of, uint256(assets));
} else {
```
However, if assets is negative, casting it to uint256 directly will cause assets to overflow into a huge value. This will cause _updateBalance() to revert whenever it is called to decrease a user's balance, making it impossible to withdraw from the protocol.

## Recommendation
Multiply assets by -1 first before casting to uint256:
```solidity
} else if (assets < 0) {
_decreaseBalance(_of, uint256(assets));
+ _decreaseBalance(_of, uint256(-assets));
} else {
```
Note that this method of converting int256 to uint256 does not work if assets happens to be type(int256).min. However, assets should never reach that value under normal conditions.
