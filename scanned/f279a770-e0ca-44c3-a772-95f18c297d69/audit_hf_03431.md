# [H] DPCU-1 | priceImpactDiffUsd Unclaimable For Adjusted PnL

## Summary
Severity: High
Contest weight: 0.1777
Dataset id: 18738
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the positionPnlUsd is positive but smaller than the priceImpactDiffUsd, the adjustedPositionPnlUsd is set to 0. However the condition for accounting for the pnlDiffAmount and making that amount claimable for the user is dependent on adjustedPositionPnlUsd > 0. Therefore, cases where the priceImpactDiffUsd cannot be entirely fulfilled by the positionPnlUsd result in the user being unable to claim their pnl that was used to cover a portion of the priceImpactDiffUsd.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/7c338222fba97d32974536618c167aa3114009e1/test/guardian/PoCs.ts#L129

## Recommendation
Change the condition to adjustedPositionPnlUsd ≥ 0 or make the incrementClaimableCollateralAmount call directly when the PnL is decreased by the priceImpactDiffUsd.
