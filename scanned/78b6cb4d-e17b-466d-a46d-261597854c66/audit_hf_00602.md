# [H] H-01 | Guaranteed Proﬁt By Rebalancing

## Summary
Severity: High
Contest weight: 0.2552
Dataset id: 2101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rebalance function removes the protocol-owned liquidity, updates ticks, and redeploys liquidity
using new tick ranges. The _updateTicks logic determines the anchorTick based on whether the
anchor liquidity is higher or lower than the discovery liquidity.
There are immediate arbitrage opportunities by using the rebalance functionality. When the anchor
liquidity is higher than the discovery liquidity:
• The upper anchor tick is below the active tick, and the current price is within the discovery range.
• User can buy a large amount of bToken, pushing the price even higher.
• Call rebalance, which updates ticks and range liquidities.
• Sell the same amount of bToken at a higher average price due to higher anchor liquidity.
A similar arbitrage opportunity can occur in the opposite direction as well. When anchor liquidity is
lower than discovery liquidity, the user can sell, rebalance, and buy back. This time, the user sells in a
low-liquidity environment and buys back in a high-liquidity environment.

## Recommendation
Consider rate limiting the amount of ticks that can be dropped at a time to limit the scale of this
arbitrage vector.
