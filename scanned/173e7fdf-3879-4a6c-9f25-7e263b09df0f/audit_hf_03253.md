# [C] DPU-1 | Open Interest Errantly Increased

## Summary
Severity: Critical
Contest weight: 0.1468
Dataset id: 17872
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The call to MarketUtils.applyDeltaToOpenInterestInTokens applies the positive sizeDeltaInTokens to the open interest in tokens while the position is being decreased by that amount of tokens rather than increased. This incorrectly represents the accounting of the decrease order and perturbs all open interest, pnl and reserves accounting for that market.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L428

## Recommendation
Negate the sizeDeltaInTokens, as these tokens are being removed from the open interest.
