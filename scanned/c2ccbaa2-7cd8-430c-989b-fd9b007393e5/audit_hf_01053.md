# [H] MJR-5 Missed depositary check

## Summary
Severity: High
Contest weight: 0.0311
Dataset id: 4029
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In function buy defined at CollateralMarket.sol#L120 contract exchanges collateral tokens to stable tokens. But in case of wrong depositary that code will lead to collateralization disbalance, that is bad even you have manual depositary changing mechanism because issuer requires exact list of depositaries and transaction wont fail because rebalance call is fault tolerance.

## Recommendation
We recommend check depositary
