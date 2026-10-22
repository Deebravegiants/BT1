# [M] Improved Precision Calculation in Trading Fee Calculation

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 12590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SafeMath is a Solidity math library that is designed to support safe math operations by preventing common overflow or underflow issues when working with uint256 operands. While it indeed blocks common overflow or underflow issues, the lack of float support in Solidity may introduce another subtle, but troublesome issue: precision loss. In this section, we examine one possible precision loss source that stems from the default division behavior, i.e., the floor division. Conceptually, the floor division is a normal division operation except it returns the largest possible integer that is either less than or equal to the normal division result. In SafeMath, floor(x) or simply div takes as input an integer number 푥 and gives as output the greatest integer less than or equal to 푥, denoted floor(x) = 푥. Its counterpart is the ceiling division that maps 푥 to the least integer greater than or equal to 푥, denoted as ceil(x) = 푥. In essence, the ceiling division is rounding up the result of the division, instead of rounding down in the floor division. During the analysis of an internal function, i.e., _dealWithPoolAndCollectFee(), that makes a deal with the pool and then collects necessary fee, we notice the fee calculation results in (small) precision loss. For elaboration, we show the related code snippet below.
```solidity
// make real deal with the pool and then collect fee, which will be added to AMM pool
function _dealWithPoolAndCollectFee(Context memory ctx, bool isBuy) internal returns (uint) {
    (uint outpoolTokenReserve, uint inpoolTokenReserve, uint otherToTaker) = (ctx.reserveMoney, ctx.reserveStock, ctx.dealMoneyInBook);
    if (isBuy) {
        (outpoolTokenReserve, inpoolTokenReserve, otherToTaker) = (ctx.reserveStock, ctx.reserveMoney, ctx.dealStockInBook);
    }
    // all these 4 variables are less than bits
    // outAmount is sure to less than outpoolTokenReserve (which is ctx.reserveStock or ctx.reserveMoney)
    uint outAmount = (outpoolTokenReserve * ctx.amountIntoPool) / (inpoolTokenReserve + ctx.amountIntoPool);
    if (ctx.amountIntoPool > 0)
        _emitDealWithPool(uint112(ctx.amountIntoPool), uint112(outAmount), isBuy);
    uint32 feeBPS = IOneSwapFactory(ctx.factory).feeBPS();
    // the token amount that should go to the taker,
    // for buy-order, it's stock amount; for sell-order, it's money amount
    uint amountToTaker = outAmount + otherToTaker;
    require(amountToTaker < uint(1<<112), "OneSwap: AMOUNT_TOO_LARGE");
    uint fee = amountToTaker * feeBPS / 10000;
    amountToTaker -= fee;
    if (isBuy) {
        ctx.reserveMoney = ctx.reserveMoney + ctx.amountIntoPool;
        ctx.reserveStock = ctx.reserveStock - outAmount + fee;
    } else {
        ctx.reserveMoney = ctx.reserveMoney - outAmount + fee;
        ctx.reserveStock = ctx.reserveStock + ctx.amountIntoPool;
    }
    address token = ctx.moneyToken;
    if (isBuy) token = ctx.stockToken;
    _safeTransfer(token, ctx.order.sender, amountToTaker, ctx.ones);
    return amountToTaker;
}
```
The fee calculation is performed via fee = amountToTaker * feeBPS / 10000 (line 1086). Apparently, it is a standard floor() operation that rounds down the calculation result. Note that in an AMM-based DEX scenario where a user trades in one token for another, if there is a rounding issue, it is always preferable to calculate the trading amount in a way towards the liquidity pool to protect the liquidity providers' interest. Therefore, depending on specific cases, the calculation may often need to replace the normal floor division with ceiling division. In other words, the fee calculation is better revised as fee = (amountToTaker * feeBPS + 9999) / 10000, a ceiling division.

## Recommendation
Revise the logic accordingly to round-up the fee calculation.
