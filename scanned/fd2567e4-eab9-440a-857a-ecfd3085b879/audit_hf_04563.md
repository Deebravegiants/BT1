# [H] H-09 | Liquidators Can Avoid Bad Debt Socialization

## Summary
Severity: High
Contest weight: 0.1982
Dataset id: 22166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation of a borrower, bad debt is only realized when the borrower has zero leftover collateral (see FraxlendPairCore.sol: 1130). This allows a liquidator to liquidate just enough shares such that a dust amount of collateral is left behind. Thereafter, there might be little to no incentive for other liquidators to liquidate the borrower as the gas cost to do so exceeds the collateral value. As a result, the bad debt is not socialized and lenders may exit the system without any losses. The liquidator himself may be a lender and therefore incentivized to exploit this loophole.

## Proof of Concept
https://github.com/GuardianAudits/peapods-1/pull/10/commits/68f04e2ef00abb83c1373d944b4f702619744084

## Recommendation
Consider implementing a threshold for collateral remaining after liquidation, such that a liquidator must leave sufficient collateral behind if doing a partial liquidation.
