# [M] Unredeemable Collateral Upon Token Expiry

## Summary
Severity: Medium
Contest weight: 0.1227
Dataset id: 14267
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function redeemCollateral() is callable by a KPI Token holder that has registered their redemption intent and burned their KPI Tokens through the function registerRedemption(). The function conducts several checks, including preventing the call when _isExpired() is true. This check is potentially incorrect. If the user has called registerRedemption() but does not call redeemCollateral() before the token expires, they will never be able to redeem their collateral tokens. Another indication that the check on line [665] is incorrect is that the function has a condition where it checks whether the token is expired or not on line [675]. Based on the current implementation, once the contract expires (i.e., when expired() == True holds), there is no way to finalise the contract.

## Recommendation
The testing team recommends removing the instructions on line [665] to allow the burned token (through function registerRedemption()) to be redeemed.
