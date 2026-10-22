# [M] Withdrawals can silently fail

## Summary
Severity: Medium
Contest weight: 0.6533
Dataset id: 6223
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling emergencyWithdraw for a certain beneficiary it does make an external call trying to send ETH to the beneficiary specified:
```solidity
function emergencyWithdraw(address asset, uint256 amount, address beneficiary) external onlyOwner {
    settleNativeOrToken(amount, asset, beneficiary, address(this));
}
```
Inside this call, if there was an unsuccessful transfer, it would return false, which it is not checked for after.
```solidity
if (asset == address(0)) {
    (bool sent, ) = beneficiary.call{value: amount}("");
    return sent;
}
```

## Recommendation
Check that the return was not false, if so, revert.
```solidity
function emergencyWithdraw(address asset, uint256 amount, address beneficiary) external onlyOwner {
    require(settleNativeOrToken(amount, asset, beneficiary, address(this)), "transfer failed");
}
```
