# [H] OBU-2 | Cannot Only Increase Position Collateral

## Summary
Severity: High
Contest weight: 0.1623
Dataset id: 17858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The price calculation in getExecutionPrice divides by the sizeDeltaUsd, therefore reverting when the sizeDeltaUsd is 0. This results in users not being able to increase their collateral without increasing the size of their position. If a user were rushing to increase their collateral to avoid liquidation, the transaction would revert and the user would likely not be able to figure out why before their position becomes liquidated.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L2091

## Recommendation
Refactor the getExecutionPrice logic to allow for a sizeDeltaUsd of 0.
