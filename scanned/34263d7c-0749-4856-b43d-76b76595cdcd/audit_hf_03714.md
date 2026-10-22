# [M] When underlying collateral tokens are paused,

## Summary
Severity: Medium
Contest weight: 0.4536
Dataset id: 19830
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When underlying collateral tokens are paused (e.g. USDC), orders can't be
canceled, and will be executed immediately after unpause
Part of canceling an order is the sending back of the tokens provided. If the token
is paused, the sending back will revert, preventing the cancellation.
If the order was a market increase order, the user gets a free look into future prices,
and can decide after the token unpauses, whether to cancel the order or not, at the
expense of the other side of the trade.
For market orders, if the order reverts (e.g. due to the token being paused), the
error handler attempts to cancel the order so that the user doesn't get to keep the
block number (and therefore the price) that they submitted at:
```solidity
// File: gmx-synthetics/contracts/exchange/OrderHandler.sol :
OrderHandler._handleOrderError()
    Order.Props memory order = OrderStoreUtils.get(dataStore, key);
    bool isMarketOrder =
    BaseOrderUtils.isMarketOrder(order.orderType());

    if (isMarketOrder) {
        OrderUtils.cancelOrder(
        dataStore,
        eventEmitter,
        orderVault,
        key,
        msg.sender,
        startingGas,
        reason,
        reasonBytes
        );
    } else {
```
For market increase or swap orders, canceling the order sends back the collateral
in the same transaction as the cancel.
An attacker can write a bot that front-runs token pauses, and submits very large
increase orders. By the time the keeper gets to execute the order, the token will be
paused, and when it tries to cancel, the cancel will revert. The attacker can watch
the price movement during the pause, and if the potential position has a gain, let
the keeper execute the order when the token gets unpaused. If the potential
position has a loss, the bot can back-run the pause with a cancel, and prevent the
keeper from opening the original position.

## Recommendation
Do not send the collateral back during the cancel - have another separate 'claim'
function for it
