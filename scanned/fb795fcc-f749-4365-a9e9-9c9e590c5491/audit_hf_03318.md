# [H] DPU-1 | Outdated Fees For Liquidation Check

## Summary
Severity: High
Contest weight: 0.1580
Dataset id: 18169
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The isPositionLiquidatable validation is checked before PositionUtils.updateFundingAndBorrowingState(params, cache.prices) is performed. Therefore the borrowing/funding fees are potentially significantly outdated when being accounted for. This leads to the liquidation keeper not being able to liquidate positions that would be liquidateable when accounting for borrowing/funding fees and ultimately exposes the market to bad debt once the fees are updated.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/DPU_1.ts

## Recommendation
Update the funding and borrowing state before checking whether the position is liquidatable.
