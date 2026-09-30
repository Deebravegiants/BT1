# [M] M-01 | Excess execution fee will be required

## Summary
Severity: Medium
Contest weight: 0.0743
Dataset id: 21905
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To deposit GM, the long token address must be 0. if (params.initialLongToken != address(0)) However, when estimating execution fees, the only way to not pay for a deposit is to have the long address equal to the market address. if (glvDeposit.market() == glvDeposit.initialLongToken()) Due to these conflicting statements, users depositing GM tokens will be required to pay an execution fee as if they were depositing the underlying asset.

## Recommendation
Consider only charging the deposit fee when an underlying long or short has been deposited.
