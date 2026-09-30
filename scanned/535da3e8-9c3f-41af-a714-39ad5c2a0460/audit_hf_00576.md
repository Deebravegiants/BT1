# [H] H-06 | GMX Callback Revert Due To Stale LLO Prices

## Summary
Severity: High
Contest weight: 0.2286
Dataset id: 2038
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol uses Chainlink LLO pricing for critical calculations during rebalance period, like getVaultPPS which fetches GmxV2PositionManager.positionMargin. However, fetching LLO prices can revert if they are stale: if (priceDeets.lastUpdatedBlockNumber < minBlockNumber) revert PriceOutsideTolerance(); Although getVaultPPS is safe as the prices are updated when rebalance period is opened and closed, this is not the case for the GmxV2PositionManager.decreasePosition which uses LLO pricing for PnL calculations. Even if prices are updated just before decreasing a position, the GMX afterOrderExecution callback will likely revert when calculating position notional during _updatePositionCache. This issue will prevent position data to be cached, specially the key parameter used to correctly calculate positionMargin.

## Proof of Concept
https://github.com/GuardianAudits/umamipositionmanager-2/pull/5

## Recommendation
Remove the pos.size calculation when caching the position notional during GMX afterOrderExecution callback, as the calculation is not used in the current implementation.
