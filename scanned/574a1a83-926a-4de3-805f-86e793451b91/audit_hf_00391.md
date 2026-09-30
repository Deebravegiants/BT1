# [M] The slippage percent is not up-

## Summary
Severity: Medium
Contest weight: 0.6824
Dataset id: 1777
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When updating open limit orders, Trading.updateOpenLimitOrder() accepts _slippageP parameter to update the slippage percent. But in the inner implementation TradingStorage.updateOpenLimitOrder() doesn't update the slippage percent.  
The slippage percent is given to the [Trading.updateOpenLimitOrder()], but it is not updated in the inner implementation.  
The supports updating the slippage percent. It accepts _slippageP as a function parameter and sends the parameter to TradingStorage.updateOpenLimitOrder().  
```solidity
function updateOpenLimitOrder(
    uint _pairIndex,
    uint _index,
    uint _price,
    uint _slippageP,
    uint _tp,
    uint _sl
) external whenNotPaused {
    //...
    o.slippageP = _slippageP;
    storageT.updateOpenLimitOrder(o);
    //...
}
```
But in the implementation of, there is no code to set the slippage percent.  
```solidity
function updateOpenLimitOrder(OpenLimitOrder calldata _o) external override onlyTrading {
    if (!hasOpenLimitOrder(_o.trader, _o.pairIndex, _o.index)) {
        return;
    }
    OpenLimitOrder storage o = openLimitOrders[openLimitOrderIds[_o.trader][_o.pairIndex][_o.index]];
    o.positionSize = _o.positionSize;
    o.buy = _o.buy;
    o.leverage = _o.leverage;
    o.tp = _o.tp;
    o.sl = _o.sl;
    o.price = _o.price;
    o.block = block.number;
}
```
Internal pre-conditions  
None  
External pre-conditions  
None  
Attack Path  
None  
The slippage percent is not updated even though traders try to update the slippage.

## Recommendation
It is recommended to change the code as following:  
```solidity
function updateOpenLimitOrder(OpenLimitOrder calldata _o) external override onlyTrading {
    if (!hasOpenLimitOrder(_o.trader, _o.pairIndex, _o.index)) {
        return;
    }
    OpenLimitOrder storage o = openLimitOrders[openLimitOrderIds[_o.trader][_o.pairIndex][_o.index]];
    o.positionSize = _o.positionSize;
    o.buy = _o.buy;
    o.leverage = _o.leverage;
    o.tp = _o.tp;
    o.sl = _o.sl;
    o.price = _o.price;
    o.slippageP = _o.slippageP;
    o.block = block.number;
}
```
