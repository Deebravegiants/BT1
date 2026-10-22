# [M] M-4 Missing conditionCheck modifers

## Summary
Severity: Medium
Contest weight: 0.0543
Dataset id: 10413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are two functions: ejectOwner, defined at line ejectImplant.sol#L50, and recoverSafeFunds, defined at line failSafeImplant.sol#L86. Both of them have a call to the checkConditions function inside, but there are no conditionCheck modifiers which check conditions particularly for the callable function.

## Recommendation
We recommend adding the conditionCheck modifier to the mentioned functions.
