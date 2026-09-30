# [M] MKT-2 | MarketState Not Updated Prior To Calling Pause/Unpause

## Summary
Severity: Medium
Contest weight: 0.1170
Dataset id: 19562
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a market is paused, interest no longer accrues for positions in the calculateMarketState function as the function ceases execution early if paused() is true. However, when a market is paused with the pause function, the pending interest is not accrued. Therefore, when a market is paused, the interest accrued since the last accrueLiabilities call is effectively lost, as subsequent calls to accrueLiabilities update the marketState.lastUpdate timestamp without accruing interest. Additionally, when a market is unpaused, the protocol does not ensure that accrueLiabilities is called prior to unpausing the market. This would result in the interest accrued since the last accrueLiabilities call needing to be paid, since we no longer enter the paused() is true

## Recommendation
Call the accrueLiabilities function prior to calling pause/unpause on the market
