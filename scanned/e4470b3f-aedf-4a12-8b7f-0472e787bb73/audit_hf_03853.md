# [M] Protocol is completely incompatible with USDT

## Summary
Severity: Medium
Contest weight: 0.0539
Dataset id: 20110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
USDT will revert if the current allowance is greater than 0 and an non-zero approval is made. There are multiple instances throughout the contracts where this causes issues. In some places this can create scenarios where it becomes impossible to liquidate and/or borrow it.
See summary.
USDT may become impossible to liquidate or borrow

## Recommendation
Utilize the OZ safeERC20 library and safeApprove
