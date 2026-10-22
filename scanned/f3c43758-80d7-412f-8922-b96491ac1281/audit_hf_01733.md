# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.3841
Dataset id: 9468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _fee parameter in setFee() is missing any constrains and if we have malicious or compromised owner there might be a serious problem. The comments above the declaration of fee variable says that a value of 100 is 1% fee:
```solidity
* @notice Fee value in basis points.
* @dev Value of 100 is 1% fee.
uint16 public fee;
```
but since we are missing any input validation the fee can be set to uint16 max value which is 65535. This value will be equal to ~ 650% fee. The same can happen in the constructor as well as the setFee() method is called during construction time.

## Recommendation
Set a reasonable upper constrain for fee. For example 5%, or as much as you decide: if(_fee > 500) { revert MaxFeeIs5Percent();
