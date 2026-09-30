# [H] Multiple update position requests can be cre-

## Summary
Severity: High
Contest weight: 0.6058
Dataset id: 19709
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The updateCollateral() function adjusts positions on the GMX PositionRouter to
match the target leverage of the liquidity pool. The function should only adjust
positions when there is no pending order. Otherwise, the pendingOrderKey will be
overwritten, making it impossible to cancel previous pending orders with
cancelPendingOrder(). Also, it's possible to create multiple pending orders at the
same time by calling updateCollateral() repeatedly.
When there are two positions open at the same time, then updateCollateral() can
be called repeatedly to create update position requests. The check if position
requests are allowed is only performed in _getCurrentLeverage() and checked on
line 305.
A malicious user could call updateCollateral() repeatedly and create many update
position requests in case there are two positions open at the same time. This could
unbalance the overall hedging position to the point where it gets liquidated.
```solidity
function updateCollateral() external payable virtual override nonReentrant {
    CurrentPositions memory positions = _getPositions();
    emit HedgerPosition(positions);
    if (positions.amountOpen > 1) {
        int expectedHedge = _getCappedExpectedHedge();
        _closeSecondPosition(positions, expectedHedge);
        return;
    }
    (, bool needUpdate, int collateralDelta) = _getCurrentLeverage(positions);
    if (!needUpdate) return;
}
```
oolHedger.sol#L294-L305

## Recommendation
updateCollateral() should check if there are pending orders before creating any
new requests on the GMX PositionRouter contract. So the pending order check
should occur before _closeSecondPosition() is called.
