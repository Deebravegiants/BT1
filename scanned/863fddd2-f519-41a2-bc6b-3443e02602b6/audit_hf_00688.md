# [M] M-09 | Decaying Redemption Fee Can Be Bypassed

## Summary
Severity: Medium
Contest weight: 0.1189
Dataset id: 2239
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The decayingRedemptionFee function decays the user's fee as time passes. However, the if-else statement's conditions are checked in wrong order. The code tries to set percentPassed if mintedTimestamp[user] = 0 only if percentPassed = 1e18. But if mintedTimestamp[user] = 0, the value of percentPassed will be much higher than 1e18. This can be combined with the decayingRedemptionFeeMinBaseAmount (which is currently set to 5e18) to avoid paying fees. When a user wants to exit the system, instead of redeeming and paying a decaying fee, they can transfer 5e18 of their tokens as many times as they want to a brand new account. This will result in them having all of the tokens in that new account and the mintedTimestamp = 0 = percentPassed = 1e18 and no fees being paid.

## Recommendation
Switch the if-else conditions - ﬁrst check mintedTimestamp[user] = 0 and then percentPassed > 1e18.
