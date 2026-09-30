# [M] When a position is closed, the execution fees

## Summary
Severity: Medium
Contest weight: 0.4451
Dataset id: 22883
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is decreased fully or partially, all the stop orders for that particular position will be canceled. Normally, the cancel order flow returns the execution fee paid by the user. However, this type of cancellation does not do that. As a result, all the STOP_LOSS and TAKE_PROFIT order execution fees are lost for the user.
When a position is decreased partially or in full, the DecreasePositionProcess::decreasePosition function will remove all the hanging close orders with the following line:
CancelOrderProcess.cancelStopOrders(
cache.position.account,
symbolProps.code,
cache.position.marginToken,
cache.position.isCrossMargin,
CancelOrderProcess.CANCEL_ORDER_POSITION_CLOSE,
params.requestId
);
As we can observe in CancelOrderProcess::cancelStopOrders function the order removed from the accounts storage and global storage:
```solidity
function cancelStopOrders(
address account,
bytes32 symbol,
address marginToken,
bool isCrossMargin,
bytes32 reasonCode,
uint256 excludeOrder
) external {
    ...
    if (
        orderInfo.symbol == symbol &&
        orderInfo.marginToken == marginToken &&
        Order.Type.STOP == orderInfo.orderType &&
        orderInfo.isCrossMargin == isCrossMargin
    ) {
        accountProps.delOrder(orderIds[i]);
        orderPros.remove(orderIds[i]);
    }
}
```
When the order is removed from storage user can no longer cancel it and get back the execution fee. All the stop loss and take profit orders execution fees are lost for the user.
When user decides to close positions they will lose the execution fees. It can interpreted as user mistake however, If the account is liquidated than it can't be users mistake and the execution fees are lost regardless.

## Recommendation
Refund the execution fees as it's done in a normal cancel order
