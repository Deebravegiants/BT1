# [H] Revisited TokenA Buy Price in threeThreeTradeBTC()

## Summary
Severity: High
Contest weight: 0.6356
Dataset id: 12555
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, NBC supports the unique type of (3,3) friend trade. While examining the associated trading functions, we notice a key routine makes use of a wrong price, which charges more then intended for the buying user.
To elaborate, we show below the aﬀected threeThreeTradeBTC() routine. It has a rather straightforward logic in completing the (3,3) friend request. Following the same user scenario, a user A initiates a friend request (3,3) to another user B by specifying the token amount and the maximum price after fees. And the user B has the option to (1) reject the request or (2) accept the request. If the request is accepted, both should share the equal buy price. However, our analysis shows that the user A paid buyPriceAfterFee while the user B paid buyPriceBAfterFeeMax and these two numbers are not equal (line 877).
```solidity
function threeThreeTradeBTC(
    bytes32 orderId
) external notContract nonReentrant {
    ThreeThreeTypes.Order storage order = _threeThreeOrders[orderId];
    require(
        order.status == ThreeThreeTypes.OrderStatus.Unfilled,
        "AKF_BOS"
    );
    require(order.locked, "AKF_ONL");
    require(order.amount == 0, "AKF_ONR");
    address tokenB = order.tokenB;
    address ownerB = IAlphaKeysToken(tokenB).getPlayer();
    require(_msgSender() == ownerB, "AKF_NOB");
    // save ownerB
    order.ownerB = ownerB;
    order.status = ThreeThreeTypes.OrderStatus.Filled;
    address ownerA = order.ownerA;
    address tokenA = order.tokenA;
    uint256 buyPriceBAfterFeeMax = order.buyPriceBAfterFeeMax;
    uint24 protocolFeeRatioA = IAlphaKeysToken(tokenA).getProtocolFeeRatio();
    uint24 playerFeeRatioA = IAlphaKeysToken(tokenA).getPlayerFeeRatio();
    uint256 amountA = NumberMath.getBuyAmountMaxWithCash(
        protocolFeeRatioA,
        playerFeeRatioA,
        tokenA,
        buyPriceBAfterFeeMax
    );
    uint24 protocolFeeRatioB = IAlphaKeysToken(tokenB).getProtocolFeeRatio();
    uint24 playerFeeRatioB = IAlphaKeysToken(tokenB).getPlayerFeeRatio();
    uint256 amountB = NumberMath.getBuyAmountMaxWithCash(
        protocolFeeRatioB,
        playerFeeRatioB,
        tokenB,
        buyPriceBAfterFeeMax
    );
    order.amountA = amountA;
    order.amountB = amountB;
    // AKF_BANM: buy amount not min
    require(amountA > 0 && amountB > 0, "AKF_BANM");
    address vault = _vault;
    uint256 buyPriceAfterFee = _buyKeysForV2ByToken(
        tokenB,
        vault,
        amountB,
        buyPriceBAfterFeeMax,
        ownerA,
        TokenTypes.OrderType.ThreeThreeOrder
    );
    uint256 refundAmount = buyPriceBAfterFeeMax.sub(buyPriceAfterFee);
    if (refundAmount > 0) {
        TransferHelper.safeTransferFrom(_btc, vault, ownerA, refundAmount);
    }
    _buyKeysForV2ByToken(
        tokenA,
        ownerB,
        amountA,
        buyPriceBAfterFeeMax,
        ownerB,
        TokenTypes.OrderType.ThreeThreeOrder
    );
    emit ThreeThreeTradeBTC(
        orderId,
        tokenA,
        ownerA,
        tokenB,
        ownerB,
        amountA,
        amountB
    );
    IAlphaKeysToken(tokenA).permitLock30D(ownerB, amountA);
    IAlphaKeysToken(tokenB).permitLock30D(ownerA, amountB);
}
```

## Recommendation
Improve the above routine by making use of the correct buying price.
