# [M] M-08 | Liquidations May Liquidate LPs

## Summary
Severity: Medium
Contest weight: 0.1822
Dataset id: 22113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• When a trader is liquidated all of the trader's collateral is distributed to the LPs by reallocating it to
the distributor where the funds do not contribute to the LP's health.
• After that the positions of the trader (with negative PnL) are closed.
The totalDebt is calculated with the following formula and can be negative if the LPs currently make
a profit through trader losses: totalDebt = reportedDebt - marketDepositedCollateral
Here is an example of how a liquidation could influence this calculation:
• A trader owns $1000 collateral and has a position with a $700 loss
• Before the liquidation totalDebt = 300 - 1000 = -700 (LPs make profit)
• After the liquidation totalDebt = 0 - 0 = 0 (position is neutral)
As pools delegate to multiple markets it could be that other markets have a positive totalDebt and
this negative totalDebt is needed to balance the LP's health.
Therefore this reallocation of debt to the distributor may cause some LP positions to become
immediately unhealthy as they no longer are credited with the negative debt of the position (that was
liquidated now).
Their debt and collateral would then be socialized amongst the other LP positions, however these
positions would not receive the collateral rewards that would have gone to the liquidated account
through the distributor this way.

## Recommendation
Consider restructuring the method by which market deposited collateral is distributed to LPs upon
liquidation.
