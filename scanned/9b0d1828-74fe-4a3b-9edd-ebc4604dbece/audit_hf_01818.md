# [H] Missing negation in if clause

## Summary
Severity: High
Contest weight: 0.7361
Dataset id: 10097
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When setting weights via the setWeightBands function, certain restrictions need to be followed. The weight has to be lower than the PRECISION value, which is 1e18. This is because the sum of weights must add up to 1e18. This check is incorrectly applied in the setWeightBands function.
```solidity
if ((lower_[t] <= PRECISION && upper_[t] <= PRECISION)) {
    revert Pool__BandsOutOfBounds();
```
As seen above, the contract will revert if both the weights are below PRECISION. Thus the function forces the setting of the weights to be above the 1e18 cap, which will break other parts of the system. The code in fact is missing a negation!, so the contract should revert only if the criteria is NOT satisfied, not if it is satisfied.

## Recommendation
Change the if statement to:
```solidity
if (!(lower_[t] <= PRECISION && upper_[t] <= PRECISION)) {
```
