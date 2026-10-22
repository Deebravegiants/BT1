# [M] Fees is not sent to the operator

## Summary
Severity: Medium
Contest weight: 0.7100
Dataset id: 1781
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Fees is incorrectly not sent to the operator in case of opening a limit order using the openTrade function.  
Currently sending the operator fees is used only when opening a market order or a market pnl order. Fees is send to the operator because it used to update the feed in the pyth contracts. In case of limit orders no fees is send to the operator even though the  
-avantis/blob/main/avantis-contracts/src/Trading.sol#L318  
Internal pre-conditions  
Na  
External pre-conditions  
Na  
Attack Path  
Following is openTrade function  
```solidity
function openTrade(
    ITradingStorage.Trade calldata t,
    IExecute.OpenLimitOrderType _type,
    uint _slippageP
) external payable whenNotPaused returns(uint orderId) {
    IPriceAggregator aggregator = storageT.priceAggregator();
    IPairStorage pairsStored = aggregator.pairsStorage();
    require(storageT.pendingOrderIdsCount(__msgSender()) < storageT.maxPendingMarketOrders(), "MAX_PENDING_ORDERS");
    require(
        storageT.openTradesCount(__msgSender(), t.pairIndex) +
        storageT.pendingMarketOpenCount(__msgSender(), t.pairIndex) +
        storageT.openLimitOrdersCount(__msgSender(), t.pairIndex) <
        storageT.maxTradesPerPair(),
        "MAX_TRADES_PER_PAIR"
    );
    require(t.positionSizeUSDC.mul(t.leverage) >= pairsStored.pairMinLevPosUSDC(t.pairIndex), "BELOW_MIN_POS");
    require(t.tp == 0 || (t.buy ? t.tp > t.openPrice : t.tp < t.openPrice), "WRONG_TP");
    require(t.sl == 0 || (t.buy ? t.sl < t.openPrice : t.sl > t.openPrice), "WRONG_SL");
    if (_type != IExecute.OpenLimitOrderType.MARKET && _type != IExecute.OpenLimitOrderType.MARKET_PNL ) {
        require(
            t.leverage > 0 &&
            t.leverage >= pairsStored.pairMinLeverage(t.pairIndex, false) &&
            t.leverage <= pairsStored.pairMaxLeverage(t.pairIndex, false),
            "LEVERAGE_INCORRECT"
        );
        storageT.transferUSDC(__msgSender(), address(storageT), t.positionSizeUSDC);
        uint index = storageT.firstEmptyOpenLimitIndex(__msgSender(), t.pairIndex);
        storageT.storeOpenLimitOrder(
            ITradingStorage.OpenLimitOrder(
                __msgSender(),
                t.pairIndex,
                index,
                t.positionSizeUSDC,
                t.buy,
                t.leverage,
                t.tp,
                t.sl,
                t.openPrice,
                _slippageP,
                block.number
            )
        );
        aggregator.executions().setOpenLimitOrderType(__msgSender(), t.pairIndex, index, _type);
        emit OpenLimitPlaced(__msgSender(), t.pairIndex, index, t.buy, t.openPrice, 0, _type, _slippageP, t.positionSizeUSDC);
    } else {
        (bool sent, ) = payable(operator).call{value: msg.value}("");
        require(sent, "EXECUTION_FEE_NOT_SENT");
        require(
            t.leverage > 0 &&
            t.leverage >= pairsStored.pairMinLeverage(t.pairIndex, _type == IExecute.OpenLimitOrderType.MARKET_PNL) &&
            t.leverage <= pairsStored.pairMaxLeverage(t.pairIndex, _type == IExecute.OpenLimitOrderType.MARKET_PNL),
            "LEVERAGE_INCORRECT"
        );
        storageT.transferUSDC(__msgSender(), address(storageT), t.positionSizeUSDC);
        orderId = _type == IExecute.OpenLimitOrderType.MARKET ? aggregator.getPrice(t.pairIndex, IPriceAggregator.OrderType.MARKET_OPEN) : aggregator.getPrice(t.pairIndex, IPriceAggregator.OrderType.MARKET_OPEN_PNL);
        storageT.storePendingMarketOrder(
            ITradingStorage.PendingMarketOrder(
                ITradingStorage.Trade(
                    __msgSender(),
                    t.pairIndex,
                    0,
                    0,
                    t.positionSizeUSDC,
                    0,
                    t.buy,
                    t.leverage,
                    t.tp,
                    t.sl
                ),
                0,
                t.openPrice,
                _slippageP
            ),
            orderId,
            true
        );
        emit MarketOrderInitiated(__msgSender(), t.pairIndex, true, orderId, block.timestamp);
    }
}
```
As can be seen form above when order type is reversal or momentum then no fees is sent to the operator and a new limit order is opened. Now lets see that when execute limit order function is called what happens. Following is execute limit order function  
```solidity
function executeLimitOrder(
    ITradingStorage.LimitOrder _orderType,
    address _trader,
    uint _pairIndex,
    uint _index,
    bytes[] calldata priceUpdateData
) external payable whenNotPaused onlyOperator {
    IPairStorage pairsStored = IPriceAggregator(storageT.priceAggregator()).pairsStorage();
    if (_orderType == ITradingStorage.LimitOrder.OPEN) {
        require(storageT.hasOpenLimitOrder(_trader, _pairIndex, _index), "NO_LIMIT");
    } else {
        ITradingStorage.Trade memory t = storageT.openTrades(_trader, _pairIndex, _index);
        require(t.leverage > 0, "NO_TRADE");
        require(_orderType != ITradingStorage.LimitOrder.SL || t.sl > 0, "NO_SL");
        if (_orderType == ITradingStorage.LimitOrder.LIQ) {
            uint liqPrice = pairInfos.getTradeLiquidationPrice(t.trader, t.pairIndex, t.index, t.openPrice, t.buy, t.initialPosToken, t.leverage);
            require(t.sl == 0 || (t.buy ? liqPrice > t.sl : liqPrice < t.sl), "HAS_SL");
        }else{
            require(block.timestamp - t.timestamp >= pairsStored.openCloseThreshold(t.pairIndex, t.initialPosToken.mul(t.leverage)), "EARLY_CLOSE");
        }
    }
    IPriceAggregator aggregator = storageT.priceAggregator();
    IExecute executor = aggregator.executions();
    IExecute.TriggeredLimitId memory triggeredLimitId = IExecute.TriggeredLimitId(_trader, _pairIndex, _index, _orderType);
    bool isPnl = storageT.priceAggregator().pairsStorage().getPosType(_trader, _pairIndex, _index);
    uint orderId = aggregator.getPrice(_pairIndex, _orderType == ITradingStorage.LimitOrder.OPEN ? IPriceAggregator.OrderType.LIMIT_OPEN : isPnl ? IPriceAggregator.OrderType.LIMIT_CLOSE_PNL : IPriceAggregator.OrderType.LIMIT_CLOSE);
    storageT.storePendingLimitOrder(ITradingStorage.PendingLimitOrder(_trader, _pairIndex, _index, _orderType), orderId);
    executor.storeFirstToTrigger(triggeredLimitId, __msgSender());
    emit LimitOrderInitiated(_trader, _pairIndex, orderId, block.timestamp);
    aggregator.fulfill{value: msg.value}(orderId, priceUpdateData);
}
```
As can be seen from above that the operator needs to send some eth along this function call in order to call fulfill function on aggregator as it updates the pyth price feed therefore while opening limit orders fees should be sent to the operator in case of reversal and momentum orders too.  
Operator is not paid fees in case of opening limit orders of type reversal or momentum.

## Recommendation
Modify the opentrade function as follows  
```solidity
function openTrade(
    ITradingStorage.Trade calldata t,
    IExecute.OpenLimitOrderType _type,
    uint _slippageP
) external payable whenNotPaused returns(uint orderId) {
    IPriceAggregator aggregator = storageT.priceAggregator();
    IPairStorage pairsStored = aggregator.pairsStorage();
    require(storageT.pendingOrderIdsCount(__msgSender()) < storageT.maxPendingMarketOrders(), "MAX_PENDING_ORDERS");
    require(
        storageT.openTradesCount(__msgSender(), t.pairIndex) +
        storageT.pendingMarketOpenCount(__msgSender(), t.pairIndex) +
        storageT.openLimitOrdersCount(__msgSender(), t.pairIndex) <
        storageT.maxTradesPerPair(),
        "MAX_TRADES_PER_PAIR"
    );
    require(t.positionSizeUSDC.mul(t.leverage) >= pairsStored.pairMinLevPosUSDC(t.pairIndex), "BELOW_MIN_POS");
    require(t.tp == 0 || (t.buy ? t.tp > t.openPrice : t.tp < t.openPrice), "WRONG_TP");
    require(t.sl == 0 || (t.buy ? t.sl < t.openPrice : t.sl > t.openPrice), "WRONG_SL");
    (bool sent, ) = payable(operator).call{value: msg.value}("");
    require(sent, "EXECUTION_FEE_NOT_SENT");
    if (_type != IExecute.OpenLimitOrderType.MARKET && _type != IExecute.OpenLimitOrderType.MARKET_PNL ) {
        require(
            t.leverage > 0 &&
            t.leverage >= pairsStored.pairMinLeverage(t.pairIndex, false) &&
            t.leverage <= pairsStored.pairMaxLeverage(t.pairIndex, false),
            "LEVERAGE_INCORRECT"
        );
        storageT.transferUSDC(__msgSender(), address(storageT), t.positionSizeUSDC);
        uint index = storageT.firstEmptyOpenLimitIndex(__msgSender(), t.pairIndex);
        storageT.storeOpenLimitOrder(
            ITradingStorage.OpenLimitOrder(
                __msgSender(),
                t.pairIndex,
                index,
                t.positionSizeUSDC,
                t.buy,
                t.leverage,
                t.tp,
                t.sl,
                t.openPrice,
                _slippageP,
                block.number
            )
        );
        aggregator.executions().setOpenLimitOrderType(__msgSender(), t.pairIndex, index, _type);
        emit OpenLimitPlaced(__msgSender(), t.pairIndex, index, t.buy, t.openPrice, 0, _type, _slippageP, t.positionSizeUSDC);
    } else {
        (bool sent, ) = payable(operator).call{value: msg.value}("");
        require(sent, "EXECUTION_FEE_NOT_SENT");
        require(
            t.leverage > 0 &&
            t.leverage >= pairsStored.pairMinLeverage(t.pairIndex, _type == IExecute.OpenLimitOrderType.MARKET_PNL) &&
            t.leverage <= pairsStored.pairMaxLeverage(t.pairIndex, _type == IExecute.OpenLimitOrderType.MARKET_PNL),
            "LEVERAGE_INCORRECT"
        );
        storageT.transferUSDC(__msgSender(), address(storageT), t.positionSizeUSDC);
        orderId = _type == IExecute.OpenLimitOrderType.MARKET ? aggregator.getPrice(t.pairIndex, IPriceAggregator.OrderType.MARKET_OPEN) : aggregator.getPrice(t.pairIndex, IPriceAggregator.OrderType.MARKET_OPEN_PNL);
        storageT.storePendingMarketOrder(
            ITradingStorage.PendingMarketOrder(
                ITradingStorage.Trade(
                    __msgSender(),
                    t.pairIndex,
                    0,
                    0,
                    t.positionSizeUSDC,
                    0,
                    t.buy,
                    t.leverage,
                    t.tp,
                    t.sl
                ),
                0,
                t.openPrice,
                _slippageP
            ),
            orderId,
            true
        );
        emit MarketOrderInitiated(__msgSender(), t.pairIndex, true, orderId, block.timestamp);
    }
}
```
