# [C] OBU-1 | StopLossDecrease Orders Cannot Execute

## Summary
Severity: Critical
Contest weight: 0.1644
Dataset id: 17844
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
shouldValidateAscendingPrice errantly applies to StopLossDecrease orders as well, stipulating that for long position StopLossDecrease orders, the price must be increasing over the range to be executed and the inverse for short position StopLossDecrease orders. These price range requirements are unexpected for StopLossDecrease orders and leads to them not acting as stop losses for positions, which would cause tremendous loss for traders.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L836

## Recommendation
Use a separate condition to validate the price range for StopLossDecrease orders.
