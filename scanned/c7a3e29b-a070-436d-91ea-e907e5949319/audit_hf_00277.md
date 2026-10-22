# [M] Index compensate is 0 when totalLiquidity

## Summary
Severity: Medium
Contest weight: 0.3856
Dataset id: 1423
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In IndexTemplate, function compensate, When `_amount > _value`, and `<= totalLiquidity()`, the value of `_compensated` is not set, so it gets a default value of 0:
    
```solidity
if (_value >= _amount) {
    ...
    _compensated = _amount;
} else {
    ...
    if (totalLiquidity() < _amount) {
        ...
        _compensated = _value + _cds;
    }
    vault.offsetDebt(_compensated, msg.sender);
}
```
But nevertheless, in both cases, it calls `vault.offsetDebt`, even when the`_compensated` is 0 (no else block).

## Recommendation
I think, in this case, it should try to redeem the premium (withdrawCredit?) to cover the whole amount, but I am not sure about the intentions as I didn’t have enough time to understand this protocol in depth.
Right. totalLiquidity = underlyingValue + pendingPremium.
 
I will discuss how to fix this issue with my team
