# [C] GLOBAL-3 | Referral Codes Used To Game Orders

## Summary
Severity: Critical
Contest weight: 0.2048
Dataset id: 18197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A trader is able to update their referralCode at any time by creating a new order through the ExchangeRouter. A malicious trader can submit a LimitIncrease where the fees.totalNetCostAmount will be their exact initialCollateralDeltaAmount, yielding an EmptyPosition error on execution. The malicious trader can then allow the LimitIncrease to be executed once they see that prices have moved in their favor by updating their referralCode so that their fees.totalNetCostAmount is discounted and now the order will no longer revert with the EmptyPosition error. This attack can also be executed if the tier or traderDiscountFactor is updated on a trader’s current referralCode as well.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/GLOBAL_3.ts

## Recommendation
Do not allow a trader’s totalRebateFactor or traderDiscountFactor to be updated in any way for existing orders.
