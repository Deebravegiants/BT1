# [H] H-02 | Liquidity Rebalance Arbitrage

## Summary
Severity: High
Contest weight: 0.2985
Dataset id: 2020
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _updateTicks logic intentionally assigns the anchorTick such that new bAssets are not minted
within the anchor range when the bAssets minted would be in addition to the liquidity in the
discovery range.
This is to avoid the following arbitrage attack:
• Anchor liquidity < Discovery liquidity
• An attacker makes a large sell through the discovery range and the anchor range
• Due to the instantaneous large sell, and the leveraging of the anchor liquidity, the anchor liquidity
becomes greater than the Discovery liquidity
• Now the attacker can buy back the same amount of bAssets but at a lower average price because
of the increased Anchor liquidity relative to the liquidity they sold through.
There is however another similar arbitrage attack which is not protected against:
• Anchor liquidity < Discovery liquidity
• Instead of selling through the discovery range, the attacker sells from the top of the Anchor range
• After the sell, the rebalance causes the higher liquidity discovery range to come down closer to the
new price
• Now the attacker can buy back the same amount of bAssets but at a lower average price because
of the increased Discovery liquidity relative to the liquidity they sold through.
• As long as the leveraging of the Anchor position is not greater than the liquidity difference between
the Anchor and Discovery then this arbitrage is profitable.

## Recommendation
Consider rate limiting the amount of ticks that can be dropped at a time to limit the scale of this
arbitrage vector.
