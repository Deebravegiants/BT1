# [H] PPU-2 | Price Impact For Trader != Price Impact For Pool

## Summary
Severity: High
Contest weight: 0.1145
Dataset id: 18168
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a price‑impact mismatch between what a trader sees and what the impact pool records. The contract calculates the trader’s USD price impact using the execution price of the trade, but the pool’s accounting uses the latest market price stored in the contract (_latestPrice). Because the two prices can differ when the market moves between order submission and execution, the amount deducted from or added to the pool does not equal the amount reflected in the trader’s trade. This discrepancy originates from an incorrect formula on line 182 where priceImpactUsd is derived from size * priceDiff / _latestPrice instead of size * priceDiff / executionPrice. An attacker can exploit the mismatch by opening positions when the market is volatile, causing the pool to record a larger outflow or inflow than the trader actually experiences. Over multiple trades the pool’s internal accounting drifts, leading to inconsistent balances, potential loss of liquidity, and unfair pricing for honest users. The issue appears only when the price changes between the moment a trade is priced and the moment it is settled, which is common in fast‑moving markets. Traders, liquidity providers, and the protocol itself are affected because the pool may become under‑collateralised or over‑collateralised without any obvious on‑chain alarm. The problem was discovered during a formal audit by the Guardian team, which provided a proof‑of‑concept test that demonstrated the divergence growing over time. It is hard to notice because the differences may be small on a per‑trade basis and only become significant after many trades, making the accounting inconsistency look like normal market variance. To remediate, the price‑impact calculation should consistently use the execution price (the price actually applied to the trade) for both the trader’s impact and the pool’s accounting, for example by replacing the current formula with int256 priceImpactUsd = size.toInt256() * priceDiff / executionPrice.toInt256(). This ensures that the amount taken from or added to the pool matches the trader’s perceived impact, preserving accounting integrity and preventing fund drift.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/PPU_2.ts

## Recommendation
Consider using int256 priceImpactUsd = size.toInt256() * priceDiff / executionPrice.toInt256() instead of int256 priceImpactUsd = size.toInt256() * priceDiff / _latestPrice.toInt256() on line 182.
