# [H] Revisited Market-Closing Logic in HSTradingCallbacks

## Summary
Severity: High
Contest weight: 0.6360
Dataset id: 12258
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Holdstation protocol provides a non-custodial derivative trading service with normal functions to open and close user positions. While examining the close-related logic, we notice the implementation may not use the latest price feed.

In the following, we examine an example routine closeTradeMarketCallback(). As the name indicates, this routine is designed to close a user position. We notice there is an internal variable levPosUsdc which represents current leveraged position (of the given user) denominated in USDC. This variable is calculated as (t.initialPosToken * i.tokenPriceUsdc * t.leverage)/ PRECISION (line 263). Our analysis shows that this calculation uses the stale token price tokenPriceUsdc that was saved when the position is opened. Note the same issue aﬀects another related routine, i.e., executeNftCloseOrderCallback().

```solidity
function closeTradeMarketCallback(AggregatorAnswer memory a) external onlyPriceAggregator notDone {
    StorageInterfaceV5.PendingMarketOrder memory o = storageT.reqID_pendingMarketOrder(a.orderId);
    if (o.block == 0) {
        return;
    }
    StorageInterfaceV5.Trade memory t = storageT.openTrades(o.trade.trader, o.trade.pairIndex, o.trade.index);
    if (t.leverage > 0) {
        StorageInterfaceV5.TradeInfo memory i = storageT.openTradesInfo(t.trader, t.pairIndex, t.index);
        AggregatorInterfaceV6 aggregator = storageT.priceAggregator();
        PairsStorageInterfaceV6 pairsStorage = aggregator.pairsStorage();
        Values memory v;
        v.levPosUsdc = (t.initialPosToken * i.tokenPriceUsdc * t.leverage) / PRECISION;
        v.tokenPriceUsdc = aggregator.tokenPriceUsdc();
    }
}
```

In the meantime, when a user trade is unregistered, the protocol computes the remaining USDC value (usdcLeftInStorage) by deducting various fees from the position value. The purpose here is to credit the trader if the trade is winning or make necessary charges if the trade is losing. We notice this remaining USDC amount is currently computed as usdcLeftInStorage = currentUsdcPos - v.reward3 - v.reward2 (line 648), which should be revised as follows: usdcLeftInStorage = currentUsdcPos - v.reward3 - v.reward2 - v.reward1.

Public

## Recommendation
Revise above routines to compute the right position value with latest oracle prices.
