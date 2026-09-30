# [M] Incorrect Spread Percentage

## Summary
Severity: Medium
Contest weight: 0.1358
Dataset id: 1783
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the fulfill function of the PriceAggregator contract, the spread percentage (spreadP) for orders of type MARKET_OPEN_PNL is incorrectly derived. Instead of fetching the spread for PnL-based orders, the function defaults to using the spread percentage for regular orders. PriceAggregator.sol#L185 The issue lies in the fulfill function where spreadP is set using pairsStorage.pairSpreadP(r.pairIndex,false), regardless of the OrderType. When OrderType.MARKET_OPEN_PNL is used, the PnL-based spread should instead be retrieved with pairsStorage.pairSpreadP(r.pairIndex, true). if (answers.length > 0) { ICallbacks.AggregatorAnswer memory a = ICallbacks.AggregatorAnswer( orderId, _median(answers), pairsStorage.pairSpreadP(r.pairIndex, false) // Issue: Not distinguishing between PnL-based orders ,→ ); Internal pre-conditions External pre-conditions Attack Path improper spread percentage usage for pnl Order type

## Recommendation
Update the fulfill function to check the OrderType before determining the spread percentage
