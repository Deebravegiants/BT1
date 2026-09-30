# [M] M-13 | Gaming Capped Pnl By Increasing Position

## Summary
Severity: Medium
Contest weight: 0.1215
Dataset id: 2113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Traders’ PnL is capped based on _adlMaxPnlRate, and the capped PnL is used when realizing profits. uint256 maxPnlRate = _adlMaxPnlRate(marketId); uint256 maxPnlUsd = (size * entryPrice) / 1e18; maxPnlUsd = (maxPnlUsd * maxPnlRate) / 1e18; The capped PnL is calculated as above, with maxPnlUsd being directly influenced by the average entry price and the position size. When a trader’s PnL is higher than the capped PnL, the trader can intentionally increase their position at the current price just before closing it, then immediately close the position. This will result higher profit for the trader without any additional risk since both the size and entryPrice are momentarily inflated by the trader, causing maxPnlUsd to be higher.

## Recommendation
Consider implementing a grace period before allowing a position to be closed when a trader increases their initial position. This measure would discourage malicious traders by introducing an increased risk of loss during the grace period.
