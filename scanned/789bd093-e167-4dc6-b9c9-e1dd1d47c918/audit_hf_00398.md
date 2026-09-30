# [M] Loss protection inconsistency

## Summary
Severity: Medium
Contest weight: 0.2364
Dataset id: 1784
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In skewed market, users can have loss protection of 10%-20%. Based on the provided docs, the loss protection should work as follows: Example 2 (Directional Trader): If the net PnL of the above trader is -20%, then technically the trader should have lost $2,000 (20% $10K). However, with loss protection, the trader only loses $2000 * (1-20%) = $1,600. This is the magic of loss protection ! However, the current implementation works slightly different. function getTradeValuePure( uint collateral, int percentProfit, uint rolloverFee, uint closingFee, uint lossProtection ) public view returns (uint, int, uint) { int pnl = (int(collateral) * percentProfit) / int(_PRECISION) / 100; int lossProtectedPnl = pnl; if (pnl < 0) { lossProtectedPnl = (pnl * int(lossProtection)) / 100; } int fees = int(rolloverFee) + int(closingFee); int value = int(collateral) + lossProtectedPnl - fees; if (value <= (int(collateral) * int(100 - liqThreshold)) / 100) { value = lossProtectedPnl - pnl; lossProtectedPnl = fees - int(collateral) + value; } return (value > 0 ? uint(value) : 0, lossProtectedPnl, uint(fees)); } We can see that if the value is less than 15% of the collateral, the value paid out to the user is the delta of the lossProtectedPnl-pnl. Consider the following situation: 1. User has opened a $10k position with loss protection of 10%. 2. Position's current pnl is -95%. This would make the lossProtectedPnl equal to 85.5%. For simplicity we ignore the margin/ rollover fees. 3. This would cause us to enter the if-statement. Then the value assigned to the position would be -$8550-(-9500)=$950. 4. According to the example above, the position's value should've been $10000-0.9*(9500)=$1450. Instead it is just $950, resulting in $450 extra loss to the user. This is an extra loss of $450, or the user receiving ~35% less than supposed to. Wrong calculation of position's value Affected Code PairInfos.sol#L671 Loss of funds

## Recommendation
Fix is non-trivial
