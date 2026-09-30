# [M] Incorrect closing fee calcula-

## Summary
Severity: Medium
Contest weight: 0.1667
Dataset id: 1763
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the Avantis documentation (doc), the closing fee should be based on the adjusted position size:
AdjustedPositionSize=TotalPositionSize+AccruedPnL-AccumulatedMarginFee
The documentation provides a clear example:
if a trader puts up $100 of collateral at a 30x leverage, then the total position size would be $3,000. After deducting the opening fee (and assuming no change in the price of the underlying asset), the leveraged position size with an accumulated margin fee on the position of $10 is $(3000-10)=$2990. Hence, the closing fee is 2990*0.08%=$2.392.
However, during closing fee calculation, the AccumulatedMarginFee (rollover fee) is not deducted as expected.
In the TradingCallbacks contract, where AdjustedPositionSize is calculated during position closing, the AccumulatedMarginFee is not accounted for and does not reduce the position size (here and here).
This leads to users paying higher closing fees than they should.
Internal pre-conditions
None.
External pre-conditions
None.
Attack Path
1. User closes their position.
2. Closing fees are overinflated.
• Incorrect closing fee calculations result in users losing funds.
• Documentation discrepancy.

## Recommendation
Correctly reduce the AdjustedPositionSize by the accumulated rollover fee as described in the documentation.
