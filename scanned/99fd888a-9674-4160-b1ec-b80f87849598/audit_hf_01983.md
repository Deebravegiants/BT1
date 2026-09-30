# [H] OstiumTrading::removeCollateral() can be called twice in a row to obtain huge leverage values

## Summary
Severity: High
Contest weight: 0.5688
Dataset id: 11145
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OstiumTrading::removeCollateral() does not check if there are pending remove collateral, nor OstiumTradingCallbacks::handleRemoveCollateral() checks if the resulting leverage is bigger than the maximum, allowing users to call the function twice in a row to increase their leverage to huge values. This allows users to remove their whole collateral while keeping the same exposure, having very little risk.
As can be seen in the profit calculation below, the increased leverage will mean the huge gets a huge profit, getting risk free trades.
```solidity
function currentPercentProfit(
...
) private pure returns (int256 p) {
    int256 maxPnlP = int16(MAX_GAIN_P) * int32(PRECISION_6);
    p = (buy ? currentPrice - openPrice : openPrice - currentPrice) * int32(PRECISION_6) * initialLeverage / openPrice;
    p = p > maxPnlP ? maxPnlP : p;
    p = p * leverage / initialLeverage;
}
```

## Recommendation
Either check if there are pending stored remove collateral orders or check the leverage when fulfilling the order.
