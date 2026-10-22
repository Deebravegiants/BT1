# [M] M-2 Gas overﬂow during iteration (DoS)

## Summary
Severity: Medium
Contest weight: 0.0542
Dataset id: 196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each iteration of the cycle requires a gas ﬂow.
A moment may come when more gas is required than it is allocated to record one block. In this case, all iterations of the loop will fail.
Affected lines:
• ERC20Farmable.sol#L70
• ERC20Farmable.sol#L117
• ERC20Farmable.sol#L121
• ERC20Farmable.sol#L137

## Recommendation
It is recommended to add a check for the maximum possible number of elements of the arrays.
