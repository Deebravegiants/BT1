# [C] DPU-3 | Incorrect Fee Decrement

## Summary
Severity: Critical
Contest weight: 0.1641
Dataset id: 17874
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the condition where the values.outputAmount is intended to be subtracted from the fee amount, the values.outputAmount is set to 0 before being subtracted from the fee amount, causing the fee to be taken from both the outputAmount and the user’s collateral. In the case of large fees, this can lead to significant loss of assets for users interacting with the exchange, and can potentially cause unexpected accounting within a market.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L645

## Recommendation
Set the values.outputAmount to 0 after subtracting it from the fees.totalNetCostAmount.
