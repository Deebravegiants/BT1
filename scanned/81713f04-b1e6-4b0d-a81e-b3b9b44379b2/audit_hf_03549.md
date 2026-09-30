# [M] MKTM-1 | Incorrect updatedAt Assigned

## Summary
Severity: Medium
Contest weight: 0.0962
Dataset id: 19351
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the updateMarketUpload functions for both the perp prices and sumUnitaryFundings the lastMarkPriceUpdated and lastFundingUpdated are set to the block.timestamp. However, these attributes ought to be set to the perpPrice.timestamp and sumUnitaryFunding.timestamp as these are the timestamps from which the data was recorded. Using the block.timestamp for the lastFundingUpdated and lastMarkPriceUpdated values is not in line with the logic in the Ledger.executeProcessValidatedFutures function where the lastFundingUpdated is assigned to the trade.timestamp rather than the block.timestamp.

## Recommendation
Replace the cfg.setLastFundingUpdated(block.timestamp) lines with cfg.setLastFundingUpdated(data.timestamp).
