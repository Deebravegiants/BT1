# [H] Incorrect implementation of the

## Summary
Severity: High
Contest weight: 0.7555
Dataset id: 22876
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The updatePositionFromBalanceMargin() function does nothing when position.initialMarginInUsd == position.initialMarginInUsdFromBalance && amount < 0. However, in this case, the function should actually reduce the initialMarginInUsdFromBalance of the position. In the updatePositionFromBalanceMargin() function, when amount < 0, it should reduce the value of initialMarginInUsdFromBalance for the position. However, as shown at L309, the function does nothing when position.initialMarginInUsd == position.initialMarginInUsdFromBalance && amount < 0. Consequently, if users withdraw their assets, the margin amounts of the positions are not reduced accordingly. This results in users being able to utilize more tokens than they have deposited.
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
    [...]
}
```
As a result, users may be able to utilize more tokens than they have deposited.

## Recommendation
```solidity
if ((position.initialMarginInUsd == position.initialMarginInUsdFromBalance && amount > 0) || amount == 0) {
    changeAmount = 0;
    return 0;
}
```
