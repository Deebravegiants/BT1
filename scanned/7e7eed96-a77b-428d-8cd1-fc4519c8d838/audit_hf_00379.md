# [M] The trader might get liquidated

## Summary
Severity: Medium
Contest weight: 0.4593
Dataset id: 1765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In certain cases, the trader could get liquidated when attempting to close their position, resulting in a portion of their collateral being seized.
A trader's position will be liquidated if their PnL loss exceeds 85% of the collateral. When the trader closes the position, several fees are incurred, such as closing fees, margin fees, and limit close fees (only if the user has set take-profit or stop-loss limits).
When a trader’s position is liquidated or closed, the following check in getTradeValuePure determines the action based on the position's value.
```solidity
if (value <= (int(collateral) * int(100 - liqThreshold)) / 100) {
    value = lossProtectedPnl - pnl;
    lossProtectedPnl = fees - int(collateral) + value;
}
```
This check ensures that if the position is liquidated, the user receives nothing (if there is no loss rebate). If the position is closed, they receive the remaining value after accounting for PnL and fees.
However, the above check calculates value as int value = int(collateral) + lossProtectedPnl - fees, where fees represent the total fees:
total fees = closing fee + margin fee + limit close fee (if the trader opts for TP or SL)
The trader should be liquidated when their position loss exceeds 85% of the collateral.
Suppose the trader closes their position with a loss of x% of the collateral and the total fees incurred for closing the position is y.
This issue occurs when:
y > 85% of collateral - x% of collateral
• In PairInfos.sol:671 the check for liquidation compares the position's remaining value (collateral minus PnL and total fees) to the liquidation threshold (85% of collateral). However, this threshold does not include the effect of these fees, effectively lowering the trader's actual position value relative to the threshold.
Internal pre-conditions
External pre-conditions
Attack Path
1. If a user closes their position with a loss of 84% of the collateral and the total fees amount to 2% of the collateral, then the position’s value is calculated as follows:
value = collateral - pnl - total fees
value = collateral - 84% of collateral - 2% of collateral = 14% of collateral
2. Since the position value is less than 15% of the collateral, the condition is met and code block mentioned above would be executed, causing the trade to be liquidated. Their collateral is seized, and they receive no remaining value.
Trader gets liquidated if he tries to close his position loosing a part of his collateral value

## Recommendation
Update liquidation check to account for total fees while comparision
