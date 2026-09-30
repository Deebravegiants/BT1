# [M] HasEnoughSDCollateral() Check Is Performed Only Once During Onboarding

## Summary
Severity: Medium
Contest weight: 0.1292
Dataset id: 14543
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The validation of SD token quantity currently only happens during the onboarding of new validators. This process specifically involves the call to addValidatorKeys(), which further invokes checkInputKeysCountAndCollateral(), ultimately calling hasEnoughSDCollateral(). However, this value is only contingent upon the price value during onboarding, allowing users to exploit price volatility and potentially maintain fewer SD tokens than required.
This issue could adversely affect the security offered by SD tokens to users against fraudulent or negligent validators.
There is no assurance that the market value of SD collaterals will suffice over the entire staking duration. A depreciation in the market value of SD collateral could alter the staker’s incentives, making malicious activities potentially more profitable.

## Recommendation
To address this issue, the testing team recommends that stakers should cease accruing rewards until they increase the SD collateral amount to pass the hasEnoughSDCollateral() check.
