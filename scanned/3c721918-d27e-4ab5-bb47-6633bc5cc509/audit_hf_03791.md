# [M] Inadequate slippage control

## Summary
Severity: Medium
Contest weight: 0.5944
Dataset id: 20001
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current slippage control mechanism checks a user's acceptable interest rate limit against the post-trade rate, which could result in trades proceeding at rates exceeding the user's defined limit.
acts/internal/markets/InterestRateCurve.sol#L421
File: InterestRateCurve.sol
```solidity
function _getNetCashAmountsUnderlying(
    InterestRateParameters memory irParams,
    MarketParameters memory market,
    CashGroupParameters memory cashGroup,
    int256 totalCashUnderlying,
    int256 fCashToAccount,
    uint256 timeToMaturity
) private pure returns (int256 postFeeCashToAccount, int256 netUnderlyingToMarket, int256 cashToReserve) {
    uint256 utilization = getfCashUtilization(fCashToAccount, market.totalfCash, totalCashUnderlying);
    // Do not allow utilization to go above 100 on trading
    if (utilization > uint256(Constants.RATE_PRECISION)) return (0, 0, 0);
    uint256 preFeeInterestRate = getInterestRate(irParams, utilization);
    int256 preFeeCashToAccount = fCashToAccount.divInRatePrecision(
        getfCashExchangeRate(preFeeInterestRate, timeToMaturity)
    ).neg();
    uint256 postFeeInterestRate = getPostFeeInterestRate(irParams, preFeeInterestRate, fCashToAccount < 0);
    postFeeCashToAccount = fCashToAccount.divInRatePrecision(
        getfCashExchangeRate(postFeeInterestRate, timeToMaturity)
    ).neg();
```
When executing a fCash trade, the interest rate is computed based on the utilization of the current market (Refer to Line 432). The postFeeInterestRate is then computed based on the preFeeCashToAccount and trading fee, and this rate will be used to derive the exchange rate needed to convert fCashToAccount to the net prime cash (postFeeCashToAccount).
postFeeCashToAccount is the amount of cash credit or debit to an account.
If there is any slippage control in place, the slippage should be checked against the postFeeInterestRate or postFeeCashToAccount. As such, there are two approaches to implementing slippage controls:
• 1st Approach - The current interest rate is 2%. User sets their acceptable interest rate limit at 3% when the user submits the trade transaction. The user's tolerance is 1%. From the time the trade is initiated to when it's executed, the rate (postFeeInterestRate) rises to 5%, the transaction should revert due to the increased slippage beyond the user's tolerance.
• 2nd Approach - If a user sets the minimum trade return of 1000 cash, but the return is only 900 cash (postFeeCashToAccount) when the trade is executed, the transaction should revert as it exceeded the user's slippage tolerance
mempool for a period of time before executing, and thus the market condition and interest rate might change during this period, and slippage control is used to protect users from these fluctuations.
However, within the codebase, it was observed that the slippage was not checked against the postFeeInterestRate or postFeeCashToAccount.
acts/internal/markets/InterestRateCurve.sol#L405
File: InterestRateCurve.sol
```solidity
// returns the net cash amounts to apply to each of the three relevant balances.
(
    int256 netUnderlyingToAccount,
    int256 netUnderlyingToMarket,
    int256 netUnderlyingToReserve
) = _getNetCashAmountsUnderlying(
    irParams,
    market,
    cashGroup,
    totalCashUnderlying,
    fCashToAccount,
    timeToMaturity
);
..SNIP..
{
    // Do not allow utilization to go above 100 on trading, calculate the utilization after
    // the trade has taken effect, meaning that fCash changes and cash changes are applied to
    // the market totals.
    market.totalfCash = market.totalfCash.subNoNeg(fCashToAccount);
    totalCashUnderlying = totalCashUnderlying.add(netUnderlyingToMarket);
    uint256 utilization = getfCashUtilization(0, market.totalfCash, totalCashUnderlying);
    if (utilization > uint256(Constants.RATE_PRECISION)) return (0, 0);
    uint256 newPreFeeImpliedRate = getInterestRate(irParams, utilization);
..SNIP..
    // Saves the preFeeInterestRate and fCash
    market.lastImpliedRate = newPreFeeImpliedRate;
}
```
After computing the net prime cash (postFeeCashToAccount == netUnderlyingToAccount) at Line 373 above, it updates the market.totalfCash and totalCashUnderlying. Line 395 computes the utilization after the trade happens, and uses the latest utilization to compute the new interest rate after the trade and save it within the market.lastImpliedRate
acts/external/actions/TradingAction.sol#L268
File: TradingAction.sol
```solidity
function _executeLendBorrowTrade(
..SNIP..
    cashAmount = market.executeTrade(
        account,
        cashGroup,
        fCashAmount,
        market.maturity.sub(blockTime),
        marketIndex
    );
    uint256 rateLimit = uint256(uint32(bytes4(trade << 104)));
    if (rateLimit != 0) {
        if (tradeType == TradeActionType.Borrow) {
            // Do not allow borrows over the rate limit
            require(market.lastImpliedRate <= rateLimit, "Trade failed, slippage");
        } else {
            // Do not allow lends under the rate limit
            require(market.lastImpliedRate >= rateLimit, "Trade failed, slippage");
        }
    }
}
```
The trade is executed at Line 256 above. After the trade is executed, it will check for the slippage at Line 264-273 above.
Let IR1 be the interest rate used during the trade (postFeeInterestRate), IR2 be the interest rate after the trade (market.lastImpliedRate), and IRU be the user's acceptable interest rate limit (rateLimit).
Based on the current slippage control implementation, IRU is checked against IR2.
Since the purpose of having slippage control in DeFi trade is to protect users from unexpected and unfavorable price changes during the execution of a trade, IR1 should be used instead.
Assume that at the time of executing a trade (TradeActionType.Borrow), IR1 spikes up and exceeds IRU. However, since the slippage control checks IRU against IR2, which may have resettled to IRU or lower, the transaction proceeds despite exceeding the user's acceptable rate limit. So, the transaction succeeds without a revert.
This issue will exacerbate when executing large trades relative to pool liquidity.
The existing slippage control does not provide the desired protection against unexpected interest rate fluctuations during the transaction. As a result, users might be borrowing at a higher cost or lending at a lower return than they intended, leading to losses.

## Recommendation
Consider updating the slippage control to compare the user's acceptable interest rate limit (rateLimit) against the interest rate used during the trade execution (postFeeInterestRate).
