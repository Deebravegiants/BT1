# [M] Incorrect ETH tokenBase Used in OrderBook

## Summary
Severity: Medium
Contest weight: 0.4598
Dataset id: 12753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Pika protocol, the OrderBook contract is implemented to facilitate users trading with the protocol. It provides routines for traders to create/cancel orders which can be executed to open/close trades. To create an open order, the trader needs to have both the underlying token and ETH, where the underlying token is used as the margin and the ETH is used as the execution fee. Both the underlying token and ETH have their own tokenBase which is the denomination of the token. To elaborate, we show below the code snippets of the createOpenOrder() and the cancelOpenOrder() routines. As the name indicate, the createOpenOrder() routine is designed for users to create orders, and the cancelOpenOrder() routine is designed for users to cancel the created orders. While examining the token base used for ETH in these two routines, we notice the existence of possible incorrect token base used for ETH in the cancelOpenOrder() routine. Namely, the createOpenOrder() routine uses the 1e18 as the token base for ETH (line 289), while the cancelOpenOrder() routine makes use of the tokenBase as the token base for ETH (line 377). By design, the tokenBase is the token base of the collateralToken. As a result, if the collateralToken is not equal to ETH, the cancelOpenOrder() routine may use the wrong token base for ETH.
```solidity
function createOpenOrder(
    uint256 _productId,
    uint256 _margin,
    uint256 _leverage,
    bool _isLong,
    uint256 _triggerPrice,
    bool _triggerAboveThreshold,
    uint256 _executionFee
) external payable nonReentrant {
    require(_executionFee >= minExecutionFee, "OrderBook: insufficient execution fee");
    (, uint256 maxLeverage,,,,,,) = IPikaPerp(pikaPerp).getProduct(_productId);
    require(_leverage <= maxLeverage, "leverage too high");
    if (IERC20(collateralToken).isETH()) {
        IERC20(collateralToken).uniTransferFromSenderToThis((_executionFee + _margin * _leverage / BASE) * tokenBase / BASE);
    } else {
        require(msg.value == _executionFee * 1e18 / BASE, "OrderBook: incorrect execution fee transferred ");
        IERC20(collateralToken).uniTransferFromSenderToThis((_margin * _leverage / BASE) * tokenBase / BASE);
    }
    _createOpenOrder(
        msg.sender,
        _productId,
        _margin,
        _leverage,
        _isLong,
        _triggerPrice,
        _triggerAboveThreshold,
        _executionFee
    );
}

function cancelOpenOrder(uint256 _orderIndex) public nonReentrant {
    OpenOrder memory order = openOrders[msg.sender][_orderIndex];
    require(order.account != address(0), "OrderBook: non-existent order");
    delete openOrders[msg.sender][_orderIndex];
    if (IERC20(collateralToken).isETH()) {
        IERC20(collateralToken).uniTransfer(msg.sender, (order.executionFee + order.margin * order.leverage / BASE) * tokenBase / BASE);
    } else {
        IERC20(collateralToken).uniTransfer(msg.sender, (order.margin * order.leverage / BASE) * tokenBase / BASE);
    }
    payable(msg.sender).sendValue(order.executionFee.mul(tokenBase).div(BASE));
    emit CancelOpenOrder(
        order.account,
        _orderIndex,
        order.productId,
        order.margin,
        order.leverage,
        order.isLong,
        order.triggerPrice,
        order.triggerAboveThreshold,
        order.executionFee
    );
}
```
Note the same issue also exists in the executeOpenOrder()/createCloseOrder()/_createCloseOrder()/cancelCloseOrder() routines.

## Recommendation
Revise the above mentioned routines to use the consistent 1e18 as the token base for ETH.
