# [M] M-11 | GLV Oracle Count Wrong For Homogenous Markets

## Summary
Severity: Medium
Contest weight: 0.0907
Dataset id: 21892
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The estimateGlvDepositOraclePriceCount and estimateGlvWithdrawalOraclePriceCount functions add 2 constant oracle prices for every GLV. Additionally, the estimateGlvShiftOraclePriceCount is a static 4 oracle price feeds. However in the future it is planned that homogenous market GLV's may be supported. Therefore the oracle price count is consistently over-estimated for GLV's with homogenous markets. As a result users and shifts will unintentionally have to pay a higher margin to the keepers on every interaction with a homogenous market GLV.

## Recommendation
Consider adjusting the constant oracle price count for homogenous market GLVs to avoid charging excessive execution fees.
