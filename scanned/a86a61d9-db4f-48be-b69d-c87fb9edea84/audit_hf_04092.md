# [M] UAIWT-1 | Excess GM Not Partially Deposited On Supply Cap

## Summary
Severity: Medium
Contest weight: 0.1154
Dataset id: 20547
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After a deposit is created, any extra GM tokens that are received are then deposited into Dolomite
Margin for the user. If this amount would equal or surpass the maximum allowed value for a market,
then it is entirely sent to the vault owner.
This is done in the _depositIntoDefaultPositionAndClearDeposit function from the
UpgradeableAsyncIsolationModeWrapperTrader contract.
The issue is that if the maximum is exceeded, then the entire excess is wrongly sent to the the vault
owner, instead of only the difference that causes the maxWei to be exceeded. The user may
temporarily miss out on borrowing power as even a slight excess over cap leads to transferring the
whole amount to the vault owner.

## Recommendation
Modify the _depositIntoDefaultPositionAndClearDeposit function so that it sends only the excess
that would not ﬁt into the market to the vault owner and deposit the rest into Dolomite in the user’s
account.
