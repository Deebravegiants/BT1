# [M] Operators can't be removed in case they act maliciously

## Summary
Severity: Medium
Contest weight: 0.3695
Dataset id: 6222
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the owner can whitelist certain operators which are granted certain permissions to call multiple functions:
```solidity
function setOperator(address _operator) external onlyOwner {
    operators[_operator] = true;
}
```
This lacks support to remove operators in case they act maliciously or even a mistake has been made when adding them as the boolean is hardcoded to be true.

## Recommendation
Add the ability to remove operators.
