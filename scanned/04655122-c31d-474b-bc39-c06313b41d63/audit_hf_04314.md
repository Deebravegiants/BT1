# [H] H-11 | Shorts Profit Because Of Fixed Anchor Width

## Summary
Severity: High
Contest weight: 0.1633
Dataset id: 21464
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the updated Baseline V2 system the anchor is now limited to a distinct maximum width. This introduces an arbitrage whereby shorts can make a guaranteed profit by moving price into the floor, over the liquidity gap between the anchor and floor, rebalancing liquidity to fill in the gap, and buying bAsset tokens back at a lower price as the liquidity for the discovery has filled in the previous gap in the liquidity structure.

## Proof of Concept
https://github.com/GuardianAudits/baseline-team-1-pocs/pull/20

## Recommendation
Consider removing the maximum width to reduce the severity of this arbitrage. Otherwise be aware of this potential gaming and consider reducing the discovery liquidity further when it moves in to fill a previous gap — thereby reducing the profitability of this manipulation.
