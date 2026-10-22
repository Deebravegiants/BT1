# [M] UniswapPositionFeesAreNotIncludedinAssetCalculationFor Warnings and Liquidation

## Summary
Severity: Medium
Contest weight: 0.1183
Dataset id: 15433
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Uniswap LPs earn fees for providing liquidity to Uniswap pools. These fees are, however, not taken as a part of the position’s assets when the assets are being tallied for warning via the _getAssets() function. The function only returns the borrower’s balance and pool liquidity at price points a and b as seen in the Assets struct.

Since the user’s fees are not considered, a borrower could technically have enough assets, both in liquidity and fees, but will still be deemed unhealthy and prime for liquidation. Worse, when a user is liquidated, their Uniswap positions are burned, and their fees are collected to Borrower.sol where it is eventually considered as part of the assets to put up for auction, in a way, sending the fees to the liquidators instead.

## Recommendation
It is recommended that users claim and account for their fees before evaluating their liquidation eligibility.
