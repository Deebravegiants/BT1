# [M] No slippage protection in the c

## Summary
Severity: Medium
Contest weight: 0.5787
Dataset id: 1769
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users call the closeTradeMarket() function, a new Close pending market order is created. This pending market order can only be finalized by the Operator role. Since this action may be delayed, users can be negatively impacted by market conditions.
This would be acceptable if the user action was fully within their control, such as when they control transaction gas usage.
However, as users do not control when this pending action will be completed and are unable to cancel it, they are exposed to potential fund loss.
Combining this with the fact that the protocol supports a guaranteed stop loss price, which is not respected in the case of market orders, users may experience greater losses than expected if the execution is delayed.
No slippage protection in the closeTradeMarket() function flow; the slippageP and wantedPrice parameters of the PendingMarketOrder struct are set to 0. (here)
Even if set, these parameters are not used within the TradingCallbacks.closeTradeMarketCallback() function. (here)
Internal pre-conditions
1. User has an open position in one of the guaranteed stop loss markets.
2. User sets the stop loss at 10% below the position open price.
External pre-conditions
1. There are external negative market conditions, and the user expects these to worsen over time.
2. The current loss is only 5% and is still above the guaranteed stop loss.
3. User calls closeTradeMarket(), expecting the trade to close soon.
Attack Path
1. User calls closeTradeMarket() while facing a 5% loss, expecting the trade to close shortly.
2. The Operator call is delayed, and by the time it is executed, the market has declined further, resulting in a 12% loss.
3. The guaranteed stop loss at 10% is not respected, causing the user to lose an additional 2% beyond the expected stop loss.
• User experiences a loss of funds beyond his control, which cannot be seen as user mistake.

## Proof of Concept
```solidity
function test_PocMarketCloseNoSlippage() public {
    vm.startPrank(traders[0]);
    usdc.transfer(traders[2], usdc.balanceOf(traders[0]));
    uint amount = 500e6;
    usdc.mint(traders[0], amount);
    usdc.approve(address(tradingStorage), amount);
    uint id = _placeMarketLong(traders[0], amount, btcPairIndex, 50000);
    vm.stopPrank();
    _executeMarketLong(traders[0], amount, btcPairIndex, 50000, id);
    vm.startPrank(traders[1]);
    usdc.transfer(traders[2], usdc.balanceOf(traders[1]));
    usdc.mint(traders[1], amount);
    usdc.approve(address(tradingStorage), amount);
    id = _placeMarketLong(traders[1], amount, btcPairIndex, 50000);
    vm.stopPrank();
    _executeMarketLong(traders[1], amount, btcPairIndex, 50000, id);
    vm.roll(3);
    vm.startPrank(traders[0]);
    trading.updateTpAndSl{value: mockPyth.getUpdateFee(_generateSampleUpdateDataCrypto(1, btcPairIndex, 50000))}(
        btcPairIndex,
        0,
        withPricePrecision(49500),
        withPricePrecision(51000),
        _generateSampleUpdateDataCrypto(1, btcPairIndex, 50000)
    );
    vm.startPrank(traders[1]);
    trading.updateTpAndSl{value: mockPyth.getUpdateFee(_generateSampleUpdateDataCrypto(1, btcPairIndex, 50000))}(
        btcPairIndex,
        0,
        withPricePrecision(49500),
        withPricePrecision(51000),
        _generateSampleUpdateDataCrypto(1, btcPairIndex, 50000)
    );
    vm.warp(100000);
    _setChainlinkBTC(49750); // theoretical -5%
    ITradingStorage.Trade memory _trade = tradingStorage.openTrades(traders[0], btcPairIndex, 0);
    vm.startPrank(traders[0]);
    console.log("User decides to market close at ~ -5%");
    uint closeId = trading.closeTradeMarket(btcPairIndex, 0, _trade.initialPosToken); // trader 0 decides to market close at -5%
    vm.stopPrank();
    vm.warp(15);
    _setChainlinkBTC(49400); // theoretical ~12%
    vm.recordLogs();
    console.log("Operator triggers market close at ~ -12%, even though user SL is at ~ -10%");
    _executeMarketClose(btcPairIndex, 0, 0, 49400, closeId);
    Vm.Log[] memory entries = vm.getRecordedLogs();
    int percentProfit;
    (,,,,,percentProfit,,) = abi.decode(entries[17].data, (uint, ITradingStorage.Trade, bool, uint, uint, int, uint, bool));
    console.log("User 1, without slippage protection, experienced a funds loss of an extra 2% as his stop price was not triggered");
    console2.log("User 1 percentProfit:", percentProfit);
    vm.startPrank(operator);
    vm.recordLogs();
    trading.executeLimitOrder{value: mockPyth.getUpdateFee(_generateSampleUpdateDataCrypto(1, btcPairIndex, 49400))}(
        ITradingStorage.LimitOrder.SL,
        traders[1],
        btcPairIndex,
        0,
        _generateSampleUpdateDataCrypto(1, btcPairIndex, 49400)
    );
    entries = vm.getRecordedLogs();
    (,,,,,,percentProfit,,) = abi.decode(entries[19].data, (uint, uint, ITradingStorage.Trade, ITradingStorage.LimitOrder, uint, uint, int, uint, bool));
    console.log("User 2 got his SL guaranteed");
    console2.log("User 2 percentProfit:", percentProfit);
}
```
Log output:
Logs:
User decides to market close at ~ -5%
Operator triggers market close at ~ -12%, even though user SL is at ~ -10%
User 1, without slippage protection, experienced a funds loss of an extra 2% as his stop price was not triggered
User 1 percentProfit: -121582328498
User 2 got his SL guaranteed
User 2 percentProfit: -101585531592

## Recommendation
Either respect the guaranteed stop loss in the Close market orders or introduce slippage protection to the closeTradeMarket() function.
