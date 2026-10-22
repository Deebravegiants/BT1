# [M] M-14 | BFP Market Liquidations May Liquidate LPs

## Summary
Severity: Medium
Contest weight: 0.2274
Dataset id: 2272
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the ﬂagging of a position in the BFP market, the non-sUSD collateral of the ﬂagged account is removed from the market deposited collaterals and credited to the LPs through a reward distributor. However this action will remove the LPs collateral value from the totalDebt and re-allocate it to the distributor rewards which do not contribute to a V3 account’s health. Consider the following scenario:
• A BFP position holds 2 wETH, valued at $5,000 each
• The position has a $7,000 loss and is liquidatable
• Before the liquidation totalDebt = reportedDebt - marketDepositedCollateral = $3,000 - $10,000 = -$7,000
• After the liquidation totalDebt = 0 - 0 = 0, but the LPs have received $10,000 through the reward distributor
This reallocation of debt to the distributor may cause some v3 positions to unexpectedly become immediately unhealthy as they no longer are credited with the negative debt of the BFP position that was liquidated. This may cause loss of assets for those V3 accounts as they are liquidated even though they received collateral from the liquidation that would have made position healthy. Their debt and collateral would then be socialized amongst the other v3 positions, however these positions would not receive the BFP collateral rewards that would have gone to the liquidated account through the distributor this way. Unexpected liquidations in V3 could be triggered by the wiping of a position’s debt upon ﬂagging as well. This is most likely to occur when the liquidated BFP position holds little or no collateral and is supported by position proﬁt.

## Recommendation
Consider restructuring the method by which market deposited collateral is distributed to LPs upon liquidation. One potential approach would be to keep the position’s equivalent loss amount of market deposited collateral locked, but not accounted for the market deposited amounts, and to slowly stream this amount to the rewardDistributor over time to avoid instantaneous decreases in V3 position health. Or keep this portion of the collateral locked until an arbitrary caller exchanges it with sUSD, for a fee reward. Otherwise be aware of this risk and clearly document it for V3 pool delegators.
