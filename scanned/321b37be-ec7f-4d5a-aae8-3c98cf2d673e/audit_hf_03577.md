# [M] ML-2 | findLargestPosition Uses Ordinary Price Instead Of Discounted

## Summary
Severity: Medium
Contest weight: 0.0888
Dataset id: 19556
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
findLargestPosition finds the largest position in a user's portfolio and returns it to be liquidated. The issue arises due to it using the ordinary prices from the oracle instead of the ones with applied discounts when calculating position size. This will cause some positions, which are normally of higher value but have a higher discount to still be selected over ones with a lower value and a lower discount that equates to them being worth more when liquidating: (, USD[] memory totals) = portfolio.getPortfolioValue(portfolioAssets);

## Recommendation
Consider using the discounted prices to find the position that will liquidate the most amount of assets.
