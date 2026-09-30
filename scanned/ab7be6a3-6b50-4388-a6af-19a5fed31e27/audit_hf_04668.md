# [M] The use of spot data when discounting is sub-

## Summary
Severity: Medium
Contest weight: 0.4617
Dataset id: 22413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The use of spot data when discounting is subjected to manipulation. As a result, malicious users could receive more cash than expected during redemption by performing manipulation. Since this is a zero-sum, the attacker's gain is the protocol loss. When redeeming wfCash before maturity, the _sellfCash function will be executed. Assume that there is insufficient fCash left on the wrapper to be sold back to the Notional AMM. In this case, the getPrincipalFromfCashBorrow view function will be used to calculate the number of prime cash to be withdrawn for a given fCash amount and sent to the users. The function relies on current spot data (such as interest rate, spot utilization, spot totalSupply/totalDebt, etc.) internally when computing the prime cash to be withdrawn for a given fCash. Thus, it is subjected to manipulation.
File: wfCashLogic.sol
274:
```solidity
/// @dev Sells an fCash share back on the Notional AMM
function _sellfCash(
    address receiver,
    uint256 fCashToSell,
    uint32 maxImpliedRate
) private returns (uint256 tokensTransferred) {
    (IERC20 token, bool isETH) = getToken(true);
    uint256 balanceBefore = isETH ? WETH.balanceOf(address(this)) : token.balanceOf(address(this));

    uint16 currencyId = getCurrencyId();

    (uint256 initialCashBalance, uint256 fCashBalance) = getBalances();
    bool hasInsufficientfCash = fCashBalance < fCashToSell;

    uint256 primeCashToWithdraw;
    if (hasInsufficientfCash) {
        // If there is insufficient fCash, calculate how much prime cash would be purchased if the
        // given fCash amount would be sold and that will be how much the wrapper will withdraw and
        // send to the receiver. Since fCash always sells at a discount to underlying prior to maturity,
        // the wrapper is guaranteed to have sufficient cash to send to the account.
        (/* */, primeCashToWithdraw, /* */, /* */) = NotionalV2.getPrincipalFromfCashBorrow(
            currencyId,
            fCashToSell,
            getMaturity(),
            0,
            block.timestamp
        );
        // If this is zero then it signifies that the trade will fail.
        require(primeCashToWithdraw > 0, "Redeem Failed");

        // Re-write the fCash to sell to the entire fCash balance.
        fCashToSell = fCashBalance;
    }
```
Within the CalculationViews.getPrincipalFromfCashBorrow view function, it will rely on the InterestRateCurve.calculatefCashTrade function to compute the cash to be returned based on the current interest rate model. The Notional AMM uses a two-kink interest rate model, and the interest rate is computed based on the utilization rate (https://docs.notional.finance/notional-v3/prime-money-market/interest-rate-model), as shown below. The interest rate is used to discount the fCash back to cash before maturity. In summary, a higher interest rate will cause the fCash to be discounted more, and the current cash value will be smaller. The opposite is also true (Lower interest rate => Higher cash returned). Assume that the current utilization rate is slightly above Kink 1. When Bob redeems his wfCash, the interest rate used falls within the gentle slope between Kink 1 and Kink 2. Let the interest rate based on current utilization be 4%. The amount of fCash will be discounted back with 4% interest rate to find out the cash value (present value) and the returned value is x. Observed that before Kink 1, the interest rate changed sharply. If one could nudge the utilization toward the left (toward zero) and cause the utilization to fall between Kink 0 and Kink 1, the interest rate would fall sharply. Since the utilization is computed as utilization = totalfCash/totalCashUnderlying, one could deposit prime cash to the market to increase the denominator (totalCashUnderlying) to bring down the utilization rate. Bob deposits a specific amount of prime cash (either by its own funds or flash-loan) to reduce the utilization rate, which results in a reduction in interest rate. Assume that the interest rate reduces to 1.5%. The amount of fCash will be discounted with a lower interest rate of 1.5%, which will result in higher cash value, and the returned value/received cash is y. y > x. So Bob received y - x more cash compared to if he had not performed the manipulation. Since this is a zero-sum, Bob's gain is the protocol loss. Malicious users could receive more cash than expected during redemption by performing manipulation. Since this is a zero-sum, the attacker's gain is the protocol loss.

## Recommendation
Avoid using spot data when computing the amount of assets that the user is entitled to during redemption. Consider using a TWAP/Time-lagged oracle to guard against potential manipulation.
