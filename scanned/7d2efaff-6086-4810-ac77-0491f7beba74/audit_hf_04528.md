# [M] M-09 | Liquidation Fees Not Always Covered

## Summary
Severity: Medium
Contest weight: 0.0906
Dataset id: 22092
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• Traders can provide collateral in the sUSD token and also in other tokens.
• When a user is liquidated all of the users non sUSD collateral tokens are distributed among the LPs.
• The liquidator (keeper) receives the liquidation reward in sUSD
Therefore if the liquidated user did not deposit sUSD tokens and only used other tokens as collateral
the liquidator will still be paid out in sUSD.
This will cause accrual of negative credit capacity. Once the credit capacity decreases large enough,
withdrawMarketUsd will revert and traders will not get their collateral back.

## Recommendation
Pay out the keeper in the given collateral assets.
