# [M] M-03 | Swap Fees Included In Circulating Supply

## Summary
Severity: Medium
Contest weight: 0.1176
Dataset id: 21469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol deploys liquidity to Uniswap and earns fees in both reserve token and bAsset. The protocol owned bAssets and earned bAsset fees are not intended to be part of the circulating supply.
However, swap fees in bAsset are calculated as a part of the circulating supply during bump, sweep and slide. The reason of this is circulating assets is calculated with bAssetsCirculating = BPOOL.totalSupply() - BPOOL.balanceOf(address(BPOOL));.
Previously, bAsset fees were in the BPOOL and they were excluded while subtracting the balance of BPOOL. But after remediations, those fees are in the MarketMaking contract and not excluded.
The newly issued tokens during bump is calculated based on the bAssetsCirculating, and more tokens will be issued due to this.

## Recommendation
Consider subtracting the fees stored in the marketMaking contract while calculating bAssetsCirculating.
