# [M] Incoherent handleGoldGovFees Convention in HSTradingCallbacks

## Summary
Severity: Medium
Contest weight: 0.4596
Dataset id: 12265
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Holdstation protocol has a key HSTradingCallbacks contract that is designed to perform actual trading functionalities, including the governance fee collection. While analyzing the fee collection logic, we notice it makes use of an inconsistent function call convention.

In the folowing, we show the implementation of the updateSlCallback() routine that calls storageT.handleGoldGovFees() to manage the governance fees. It comes to our attention that this handleGoldGovFees() function has ﬁve arguments and the fourth argument is an address type. However, in updateSlCallback(), the calls to storageT.handleGoldGovFees() (lines 489-490) has the fourth argument in boolean. Note this issue aﬀects a number of other routines, including openTradeMarketCallback(), closeTradeMarketCallback(), registerTrade(), and updateSlCallback().

```solidity
function updateSlCallback(AggregatorAnswer memory a) external onlyPriceAggregator notDone {
    AggregatorInterfaceV6 aggregator = storageT.priceAggregator();
    AggregatorInterfaceV6.PendingSl memory o = aggregator.pendingSlOrders(a.orderId);
    StorageInterfaceV5.Trade memory t = storageT.openTrades(o.trader, o.pairIndex, o.index);
    if (t.leverage > 0) {
        StorageInterfaceV5.TradeInfo memory i = storageT.openTradesInfo(o.trader, o.pairIndex, o.index);
        Values memory v;
        v.tokenPriceUsdc = aggregator.tokenPriceUsdc();
        v.levPosUsdc = (t.initialPosToken * i.tokenPriceUsdc * t.leverage) / PRECISION /
        // Charge in USDC if collateral storage or token if collateral in vault
        v.reward1 = t.positionSizeUsdc > 0
            ? storageT.handleGoldGovFees(t.pairIndex, v.levPosUsdc, 0, true, false)
            : (storageT.handleGoldGovFees(t.pairIndex, (v.levPosUsdc * PRECISION) / v.tokenPriceUsdc, 0, false, false) *
                v.tokenPriceUsdc) / PRECISION;
    }
}

function handleGoldGovFees(
    uint256 _pairIndex,
    uint256 _leveragedPositionSize,
    uint256 _referralFee,
    address _trader,
    bool _fullFee
) external onlyTrading returns (uint256 fee) {
    fee = (_leveragedPositionSize * priceAggregator.openFeeP(_pairIndex)) / PRECISION / 100;
    if (!_fullFee) {
        fee /= 2;
        uint256 goldFeePaid = (fee * goldFeeP) / PRECISION;
        goldFeesUsdc += goldFeePaid;
        uint256 agencyFee = 0;
        if (_referralFee == 0 && address(hsAgency) != address(0)) {
            agencyFee = hsAgency.distributeReward(2 * fee - goldFeePaid, _trader);
        }
        govFeesUsdc += (2 * fee - goldFeePaid - _referralFee - agencyFee);
        fee = fee * 2 - _referralFee;
    }
}
```

## Recommendation
Revise the above routines to provide intended arguments to handle governance fees.
