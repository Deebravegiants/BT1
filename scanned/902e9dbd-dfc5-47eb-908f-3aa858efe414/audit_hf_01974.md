# [M] OstiumTrading::closeTradeMarket() and OstiumTrading::topUpCollateral() are missing pending trigger checks

## Summary
Severity: Medium
Contest weight: 0.0451
Dataset id: 11135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OstiumTrading::closeTradeMarket() and OstiumTrading::topUpCollateral() can be used to frontrun liquidation calls whose trigger has already been set, making the liquidation fail in OstiumPriceUpKeep::performUpkeep(), draining fees and gaming the system.

## Recommendation
Add OstiumTrading::checkNoPendingTrigger() to both functions.
