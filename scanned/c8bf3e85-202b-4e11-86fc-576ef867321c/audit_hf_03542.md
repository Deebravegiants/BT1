# [H] GLPM-1 | Reduced Redemption Fees Gamed

## Summary
Severity: High
Contest weight: 0.1762
Dataset id: 19344
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _redeemGlp function, users are allowed to make any arbitrary external calls with the redemptionInfo.externalCallTargets and redemptionInfo.externalCallDataList. Therefore a user seeking to redeem GLP using the discounted redemption may do so as the external call is executed within the context of the withReducedRedemptionFees modifier. Users may abuse the system in a similar way by simply providing an EOA address as the redemptionInfo.receiver rather than the DepositVault, or by using the subsequent external call to transfer out the redeemed tokens to their EOA.

## Recommendation
Require that the redeemedTokenAmount (or at least a majority, accounting for potential fees & slippage) end up in the DepositVault contract. This validation also serves as a safety net in the event that the provided redemptionInfo.externalCallTargets or redemptionInfo.externalCallDataList hold errors.
