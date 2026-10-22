# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.3837
Dataset id: 16256
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setDepositLimit(uint256 newDepositLimit) external onlyOwner {
    //@audit not constrained in any way
    uint256 previousDepositLimit = depositLimit;
    depositLimit = newDepositLimit;
    emit DepositLimitChanged(previousDepositLimit, newDepositLimit);
}
```
The newDepositLimit parameter in setDepositLimit() is missing any constraints and if we have a malicious or compromised owner or one that does a "fat-finger", can input a huge number or a really small number. This method's argument will result in a big problem in certain functions, where depositLimit is used.

## Recommendation
Set a reasonable upper and lower constraint for newDepositLimit.
