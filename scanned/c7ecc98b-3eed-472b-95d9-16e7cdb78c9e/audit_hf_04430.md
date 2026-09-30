# [M] M-02 | GLV Withdrawal Callback Gas Cost Ignored

## Summary
Severity: Medium
Contest weight: 0.0714
Dataset id: 21906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For the GLV Withdrawal flow, the callback call is made at the end of GlvWithdrawalUtils::executeGlvWithdrawal(). Since the callback is made after payExecutionFee() is called, the gas used in the callback will not come out of the user’s execution fee and will instead be charged to GMX. The max callback gas limit is set to 3,000,000 for Arbitrum and 2,000,000 for Avalanche, which over time will cause GMX incur substantial losses.

## Recommendation
Move the callback call to before payExecutionFee() is called.
