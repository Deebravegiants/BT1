# [M] M-20 | Increased Liquidation Rewards

## Summary
Severity: Medium
Contest weight: 0.1241
Dataset id: 156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Positions will be liquidated once the price drops below the current tick price. Liquidating multiple ticks with high expo, or with a big liquidation bonus (due to where the current price is at, compared to the tick liquidation price), will grant a higher liquidation reward. However, the total ETH reward calculated should not exceed 0.5 ETH.
Therefore, it can be more profitable for a user to liquidate ticks one by one, through the initiate and validate functions (functions that will try to perform one iteration of liquidation if there are liquidatable ticks), instead of using the liquidate function that contains a capped liquidation reward.

## Recommendation
Cap the maximum rewards that can be gained from liquidations that are happening via initiate or validate functions if there are still pending liquidations.
These amounts should be capped such that the maximum reward that can be gained from individual liquidation should match with the max reward amount of multiple liquidations using liquidate.
It might be also good to consider limiting rewards that can be gained from liquidations in a single block. This can also incentivize the usage of liquidate.
