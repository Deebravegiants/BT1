# [H] Improper implementation of the

## Summary
Severity: High
Contest weight: 0.6369
Dataset id: 22875
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The updates to position values are not based on the current price of the marginToken. As shown in the code at L314 and L318, all calculations are based on percentages relative to the maximum values. They do not factor in the current price of the marginToken. Consequently, even if the current marginToken price is significantly lower than when the position was last updated, users can still update their position using the higher price.
```solidity
function updatePositionFromBalanceMargin(
    Position.Props storage position,
    bool needSendEvent,
    uint256 requestId,
    int256 amount
) public returns (uint256 changeAmount) {
    if (position.initialMarginInUsd == position.initialMarginInUsdFromBalance || amount == 0) {
        changeAmount = 0;
        return 0;
    }
    if (amount > 0) {
        uint256 borrowMargin = (position.initialMarginInUsd - position.initialMarginInUsdFromBalance)
            .mul(position.initialMargin)
            .div(position.initialMarginInUsd);
        changeAmount = amount.toUint256().min(borrowMargin);
        position.initialMarginInUsdFromBalance += changeAmount.mul(position.initialMarginInUsd).div(
            position.initialMargin
        );
    } else {
        uint256 addBorrowMarginInUsd = (-amount).toUint256().mul(position.initialMarginInUsd).div(
            position.initialMargin
        );
        if (position.initialMarginInUsdFromBalance <= addBorrowMarginInUsd) {
            position.initialMarginInUsdFromBalance = 0;
            changeAmount = position.initialMarginInUsdFromBalance.mul(position.initialMargin).div(
                position.initialMarginInUsd
            );
        } else {
            position.initialMarginInUsdFromBalance -= addBorrowMarginInUsd;
            changeAmount = (-amount).toUint256();
        }
    }
    if (needSendEvent && changeAmount > 0) {
        position.emitPositionUpdateEvent(requestId, Position.PositionUpdateFrom.DEPOSIT, 0);
    }
}
```
Users can update their positions' initialMarginInUsdFromBalance values using a price higher than the current price of the marginToken.

## Recommendation
The PositionMarginProcess.updatePositionFromBalanceMargin() function should be based on the current price of the marginToken.
