# [M] L2 sequencer down will push an auction's price

## Summary
Severity: Medium
Contest weight: 0.3877
Dataset id: 22461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol implements a L2 sequencer downtime check in the Registry. In the event of sequencer downtime (as well as a grace period following recovery), liquidations are disabled for the rightful reasons. However, while the sequencer is down, any ongoing auctions' price decay is still ongoing. When the sequencer goes back online, it will be possible to liquidate for a much lower price, guaranteeing bad debt past a certain point. While the price oracle has sequencer uptime checks, the liquidation auction's price curve calculation does not. The liquidation price is a function with respect to the user's total debt versus their total collateral. Due to no sequencer check within the liquidator, the liquidation price continues to decay when the sequencer is down. It is possible for the liquidation price to drop below 100%, that is, it is then possible to liquidate all collateral without repaying all debt. Any ongoing liquidations that are temporarily blocked by a sequencer outage will continue to experience price decay. When the sequencer goes back online, liquidation will have dropped significantly in price, causing liquidation to happen at an unfair price as well. Furthermore, longer downtime durations will make it possible to seize all collateral for less than 100. Any ongoing liquidations during a sequencer outage event will execute at a lower debt-to-collateral ratio, potentially guaranteeing bad debt and/or user being liquidated for a lower price.

## Proof of Concept
We use the default liquidator parameters defined in the constructor for our example:
• Starting multiplier is 150%.
• Half-life duration is 1 hour.
• Cutoff time is irrelevant.
Consider the following scenario:
1. Bob's account becomes liquidatable. Someone triggers liquidation start.
2. Anyone can now buy 100 of Bob's collaterals at the price of 150 of his debt. However, this is not profitable yet, so everyone waits for the price to drop a bit more.
3. After 30 minutes, auction price is now 60 of debt for 100 of collateral. Not much has moved, so this is still not profitable yet.
4. The sequencer has experienced multiple outages of this duration in the past. In 2022, there was an outage of approx. seven hours. There was also a 78-minute outage just December 2023.
5. When the sequencer goes up, the auction has been going on for 1.5 hours, or 1.5 half-lives. Auction price is now 60 of debt.
6. Liquidation is now profitable. All of Bob's collaterals are liquidated, but the buyer only has to repay 91:82 of debt for 100 of collateral but positive debt (specifically, 8:18 of Bob's original debt). The impact becomes more severe the longer the sequencer goes down. In addition, the grace period on top of it will decay the auction price even further, before the auction can be back online.
• In the above scenario, if the sequencer outage plus grace period is 2 hours, then the repaid debt percentage is only 60.
Furthermore, even if downtime is not enough to bring down the multiplier to less than 100, users will still have their collateral being sold at a lower price anyway. Therefore any duration of sequencer downtime will cause an unfair loss.

## Recommendation
Auctions' price curve should either check and exclude sequencer downtime alongside its grace period, or said auctions should simply be voided.
