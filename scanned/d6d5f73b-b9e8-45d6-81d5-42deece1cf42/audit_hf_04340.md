# [H] H-01 | Anchor Liquidity Is Incorrectly Calculated After Sweep

## Summary
Severity: High
Contest weight: 0.2144
Dataset id: 21496
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During sweep, discovery liquidity is rebalanced into anchor and floor liquidity. Anchor’s tick range is also increased. It was observed that anchor’s liquidity could decrease post-sweep which is undesirable. The issue stems from the increased anchor tick range and calling BPOOL.manageReservesFor(Range.ANCHOR, Action.ADD, newReservesA); instead of BPOOL.manageLiquidityFor(). There is no guarantee that newReservesA is sufficient to maintain or increase anchor’s liquidity, given the new tick range. Although surplusReservesD (surplus reserves in discovery) is added to newReservesA, this may not be sufficient as surplus could be small or even zero. As a result, every time sweep is called anchor liquidity could decrease, leading to a very thin anchor range and poor trading conditions where price fluctuates wildly between floor and discovery.

## Recommendation
Calculate the amount of reserves needed to maintain anchor.liquidity then add surplus reserves before re deploying Anchor liquidity.
