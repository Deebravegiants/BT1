# [C] C-02 | Free Borrowing When Collateral Is The Same Asset

## Summary
Severity: Critical
Contest weight: 0.2094
Dataset id: 2512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users deposit collateral and borrow assets using the PositionManager contract, and every action that changes a Position’s balance requires a health check via RiskEngine and RiskModule. The health check is done by comparing total debt of a position and total asset of a position. However, this health check is inaccurate when a borrowed asset and the collateral asset are the same. The RiskEngine accounts newly borrowed assets as user provided collateral, which causes the check to be incorrect. A pool owner can
• Set the ltv to 1 for the borrow asset.
• Add the borrow asset as collateral asset to his position with addToken
• Borrow all assets from the pool without adding any collateral.
Resulting in all funds to be frozen for regular depositors.

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-1/pull/12/files

## Recommendation
Do not allow borrow asset and the collateral asset to be the same.
