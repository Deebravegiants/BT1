# [M] Users can have positions with a margin lower than the minimum margin

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 22904
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Opening very small positions is not allowed. However, closing positions such that the remaining margin is minimal (dust) is possible. When positions are opened, it is strictly checked whether the position's initial margin is higher than the minimum allowed margin:
```solidity
function _validatePlaceOrder(IOrder.PlaceOrderParams calldata params) internal view {
    //..
    if (params.isCrossMargin && params.orderMargin < AppTradeConfig.getTradeConfig().minOrderMarginUSD) {
        revert Errors.PlaceOrderWithParamsError();
    }
}
```
However, positions can be closed in such a way that the remaining margin is lower than the minimum order margin in USD. There are no checks to ensure that the leftover margin will be higher than the minimum order margin in USD. Code PoC:
```typescript
it("Closing positions can end up the position in dust", async function () {
    const wbtcAmount = precision.token(10);
    await deposit(fixture, {
        account: user0,
        token: wbtc,
        amount: wbtcAmount,
    });
    const orderMargin = precision.token(100_000); // 4btc$
    usdc.connect(user0).approve(diamondAddr, orderMargin);
    const executionFee = precision.token(2, 15);
    const tx = await orderFacet.connect(user0).createOrderRequest(
        {
            symbol: btcUsd,
            orderSide: OrderSide.LONG,
            posSide: PositionSide.INCREASE,
            orderType: OrderType.MARKET,
            stopType: StopType.NONE,
            isCrossMargin: true,
            marginToken: wbtcAddr,
            qty: 0,
            leverage: precision.rate(5),
            triggerPrice: 0,
            acceptablePrice: 0,
            executionFee: executionFee,
            placeTime: 0,
            orderMargin: orderMargin,
            isNativeToken: false,
        },
        {
            value: executionFee,
        }
    );
    await tx.wait();
    const requestId = await marketFacet.getLastUuid(ORDER_ID_KEY);
    const tokenPrice = precision.price(25000);
    const usdcPrice = precision.price(1); // 1$
    const oracle = [
        {
            token: wbtcAddr,
            targetToken: ethers.ZeroAddress,
            minPrice: tokenPrice,
            maxPrice: tokenPrice,
        },
        {
            token: usdcAddr,
            targetToken: ethers.ZeroAddress,
            minPrice: usdcPrice,
            maxPrice: usdcPrice,
        },
    ];
    await orderFacet.connect(user3).executeOrder(requestId, oracle);
    let positionInfo = await positionFacet.getSinglePosition(
        user0.address,
        btcUsd,
        wbtcAddr,
        true
    );
    const tx2 = await orderFacet.connect(user0).createOrderRequest(
        {
            symbol: btcUsd,
            orderSide: OrderSide.SHORT,
            posSide: PositionSide.DECREASE,
            orderType: OrderType.MARKET,
            stopType: StopType.NONE,
            isCrossMargin: true,
            marginToken: wbtcAddr,
            qty: positionInfo.qty - BigInt(5),
            leverage: precision.rate(5),
            triggerPrice: 0,
            acceptablePrice: 0,
            executionFee: executionFee,
            placeTime: 0,
            orderMargin: orderMargin,
            isNativeToken: false,
        },
        {
            value: executionFee,
        }
    );
    await tx2.wait();
    const requestId2 = await marketFacet.getLastUuid(ORDER_ID_KEY);
    await orderFacet.connect(user3).executeOrder(requestId2, oracle);
    positionInfo = await positionFacet.getSinglePosition(
        user0.address,
        btcUsd,
        wbtcAddr,
        true
    );
    console.log("Leftover position qty", positionInfo.qty);
});
```
When positions have small amount of margin and overall qty there will be rounding errors on calculating the positions fees, pnl and many other things. Also, liquidations might not be possible for these accounts because of rounding errors or because its profitability to liquidate such small margined accounts.

## Recommendation
Check whether the remaining margin is higher than the allowed min margin
