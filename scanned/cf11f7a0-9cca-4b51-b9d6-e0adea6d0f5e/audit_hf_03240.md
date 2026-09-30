# [H] ORDU-3 | Cannot Decrease Position Collateral

## Summary
Severity: High
Contest weight: 0.1357
Dataset id: 17859
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating an order, there is no condition to handle the initialCollateralDeltaAmount for decrease orders, therefore the initialCollateralDeltaAmount is always 0 for decrease orders and it is impossible for users to decrease their collateral amount without fully closing their position.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L2195

## Recommendation
Implement a condition for the initialCollateralDeltaAmount that allows users to decrease their collateral as expected.
