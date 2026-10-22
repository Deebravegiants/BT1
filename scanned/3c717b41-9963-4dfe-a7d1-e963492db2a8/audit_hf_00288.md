# [M] Missing payable

## Summary
Severity: Medium
Contest weight: 0.0581
Dataset id: 1461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following functions are not payable but uses msg.value - therefore the function must be payable. This can lead to undesired behavior.
    
        LPool.sol, addReserves should be payable since using msg.value

Nice find! The warden has identified a function which is missing the `payable` keyword. Preventing any users from adding reserves using native ether.

## Recommendation
No recommendation
