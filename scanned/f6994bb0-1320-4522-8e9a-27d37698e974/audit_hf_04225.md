# [M] M-19 | Sudden Block Fee Increases May Cause Insolvent Liquidations

## Summary
Severity: Medium
Contest weight: 0.1245
Dataset id: 21119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
New positions are validated when the order is settled by checking if the margin minus the fees will satisfy the initial and maintenance margin checks. This fees include order, keeper, flag and liquidation fees. The issue is that the calculations of these fees rely heavily on the block.basefee and eth price, the only parameters that the protocol can't control. This base fee can range from 10-15 Gwei in a normal market scenario, up to >600 Gwei when volatility is high. Therefore, users can open LONG positions when the block base fee is low, and get liquidated a few blocks later if the base fee increases, even if the market price moves in their favor. Potentially, this can cause an insolvent liquidation for small accounts since the base fee jump might be an unpredictable stepwise change.

## Recommendation
Consider increasing the market minMarginUsd to the point that it can cover the volatility of the base fee and reduce the risk of an insolvent liquidation.
