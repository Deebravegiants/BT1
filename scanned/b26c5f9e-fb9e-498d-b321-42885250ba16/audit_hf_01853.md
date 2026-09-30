# [H] H-4 Reentrancy in optimisticGrantImplant

## Summary
Severity: High
Contest weight: 0.0969
Dataset id: 10277
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createDirectGrant function makes external calls (ETH or ERC20 transfer) before updating the approvedToken.amountSpent, which allows malicious owners of BORG_SAFE to transfer a much larger part of the funds and break the logic of the optimistic grant restrictions. optimisticGrantImplant.sol#L128

## Recommendation
We recommend using a check-effect-interaction pattern for this function or using a nonReentrant modiﬁer.
