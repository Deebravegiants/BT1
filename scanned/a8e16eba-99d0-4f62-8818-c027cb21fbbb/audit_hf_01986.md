# [C] In OstiumTradingStorage, firstEmptyTradeIndex() and firstEmptyOpenLimitIndex() overwrite index 0 if not found

## Summary
Severity: Critical
Contest weight: 0.1497
Dataset id: 11148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OstiumTradingStorage::firstEmptyTradeIndex() and OstiumTradingStorage::firstEmptyOpenLimitIndex() return index 0 if they can not find an available index. This may lead to overwriting a trade in storeTrade() if, for example, a trader has 2 trades, opens a third one via market order, but the Gov frontruns the chainlink bot OstiumPriceUpKeep() and sets _maxTradesPerPair to 2. It will overwrite the trade in the callback, more specifically in OstiumTradingCallbacks::registerTrade() and lastly in OstiumTradingStorage::storeTrade().

## Recommendation
Revert if it can not find an available open trade / limit order slot instead of returning index 0.
