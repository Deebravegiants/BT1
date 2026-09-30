# [H] Borrow()s after validateBalances()

## Summary
Severity: High
Contest weight: 0.1210
Dataset id: 8027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function borrow() can still be called in the AllocateValue and PostOps phases. As this is after validateBalances() the solver has to pay for this in _settle(). However the solver is no longer in control and would be griefed this way.  
Another risk is highlighted in the issue "Circumvent AtlETH unbonding period".

## Recommendation
The most logical would be to restrict access to borrow() in these phases. However the logic from SafetyBits doesn't work in Atlas / borrow() because the variable key isn't accessible. To solve this, the ExecutionPhase should be kept at the Atlas level.  
See issue "Locking mechanism is complicated".
