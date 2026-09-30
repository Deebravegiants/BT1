# [M] gDAIPriceSource and VoltGNSPriceSource will

## Summary
Severity: Medium
Contest weight: 0.1048
Dataset id: 19771
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
gDAIPriceSource and VoltGNSPriceSource#getPrice returns the share value in terms of DAI. If DAI were to depeg then the vault would continue to give out loans under the assumption that DAI is still worth $1.
/gDAIPriceSource.sol#L17-L19
Here we see that the price source simply returns the current share price in terms of DAI. This works fine if DAI remains pegged to $1. In the event that DAI depegs then the valuation of the gDAI collateral will be completely wrong and will result in the protocol taking on a lot of bad debt.
This issue also affects VoltGNSPriceSource because GNS will be greatly overvalued
Protocol will take on a large amount of bad debt if DAI depegs

## Recommendation
Use the DAI/USD chainlink oracle to protect against DAI variations from $1
