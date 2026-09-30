# [M] M-04 | Liquidation Fees Not Covered By non-sUSD Collateral

## Summary
Severity: Medium
Contest weight: 0.1313
Dataset id: 2261
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a liquidation is ﬂagged, the liquidator is paid out in sUSD regardless of the collateral type. liquidateCollateral() will decrement the amount of collateral and send the amount to the distributor. After, withdrawMarketUsd() is called, sending the liquidator sUSD. This will lower the credit capacity. Credit capacity is primarily affected through withdrawals and deposits, which will essentially cancel out over time (although it is expected for there to be more deposits than withdrawals). However, the negative impact on credit capacity from liquidation rewards will not be balanced out in the long run. This will cause accrual of negative credit capacity. Once the credit capacity decreases to a large enough state, withdrawMarketCollateral() will revert since it veriﬁes that the credit capacity plus the deposited collateral must be greater than 0.

## Recommendation
Pay out the liquidator in the collateral asset that has been liquidated. Make sure that reward is deducted from the distribution amount.
