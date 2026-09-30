# [H] H-01 | Chainlink’s Transmit Call Can Force A LT Position Into Liquidation

## Summary
Severity: High
Contest weight: 0.4119
Dataset id: 2250
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious user can exploit the fact that the initial transferMargin call performed during redemptions to subtract margin from the position, could use a partially stale Chainlink Price Feed. By carefully selecting the withdrawal amount (marginDelta), the attacker appears to keep the position above liquidation threshold at the stale price, but once the price feed is updated with the actual current price, the margin ends up below the threshold making it liquidatable. This exploit could be relatively easy to execute as:
• Chainlink updates the price under two circumstances: When the “heartbeat” time passes (this is one hour for most of the feeds) and if the price changes by more than the deviation threshold which is usually a value between 0.1% and 0.5% (https://data.chain.link/feeds). Therefore it should not be very uncommon to ﬁnd a Chainlink price feed that deviates 0.4% from the current price.
• The LeveragedToken contract allows pulling as much margin as Synthetix PerpsV2 does, or which is the same, as much as the resulting margin would not be lower than the liquidation margin or min. initial margin (liqMargin + liqPremium).
Given these conditions, a malicious user could:
• Perform a large deposit/mint: The attacker ﬁrst deposits a large amount of sUSD margin into the LeveragedToken contract (which also decreases the overall leverage temporarily). The LeveragedToken eventually rebalances to the desired leverage ratio.
• The attacker calls redeemFor with an off chain delayed order referencing a stale aggregator price feed. This call is executed right before the Chainlink Price Feed is updated, front-running the aggregator transmit call.
• Under the stale Chainlink Price Feed the position appears to remain safely above liquidationMargin + premium.
• A rebalance order is created however, before it is executed, as the Chainlink Price Feed was just updated to the new price, a user calls PerpsV2MarketLiquidate.flagPosition. The LeveragedToken position will be ﬂagged and the only operation enabled will be a liquidation. The previous delayed order was canceled during the ﬂagging process and can not be executed anymore.
• LeveragedToken’s position is liquidated.
The attacker could pocket the ﬂagger fee (between 2$ and 1000$) from the liquidation process. This can yield a net proﬁt for the attacker if the liquidation fee surpasses whatever leveraged tokens value they still held.

## Recommendation
Upon redeeming, the LeveragedToken contract should require a safety buffer that ensures the liquidation price is signiﬁcantly (e.g., 10%) below the current aggregator price for longs and higher than the aggregator price for shorts. Concretely:
• Compute the user’s requested redemption.
• Simulate the new margin’s “post-close liquidation price.”
• Require that liquidationPrice < (currentPrice × (1 - minBuffer)). For example, if minBuffer = 10%, then liquidationPrice < 90% of the aggregator price.
This ensures that even if the aggregator price feed is off by a small fraction (like 0.5% or 1%), the leftover margin won’t be driven immediately below the liquidation threshold when the price feed is updated with the newest price. By implementing this buffer, the system blocks partial redemptions that leave no margin for slippage or stale feed differences, thus mitigating the exploit.
