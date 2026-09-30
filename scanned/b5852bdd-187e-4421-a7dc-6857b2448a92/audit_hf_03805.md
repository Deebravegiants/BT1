# [H] Excess funds withdrawn from the money mar-

## Summary
Severity: High
Contest weight: 0.7872
Dataset id: 20019
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Excessive amounts of assets are being withdrawn from the money market.

```solidity
function _redeemMoneyMarketIfRequired(
    uint16 currencyId,
    Token memory underlying,
    uint256 withdrawAmountExternal
) private {
    // If there is sufficient balance of the underlying to withdraw from the contract
    // immediately, just return.
    mapping(address => uint256) storage store = LibStorage.getStoredTokenBalances();
    uint256 currentBalance = store[underlying.tokenAddress];
    if (withdrawAmountExternal <= currentBalance) return;

    IPrimeCashHoldingsOracle oracle = PrimeCashExchangeRate.getPrimeCashHoldingsOracle(currencyId);
    // Redemption data returns an array of contract calls to make from the Notional proxy (which
    // is holding all of the money market tokens).
    (RedeemData[] memory data) = oracle.getRedemptionCalldata(withdrawAmountExternal);

    // This is the total expected underlying that we should redeem after all redemption calls
    // are executed.
    uint256 totalUnderlyingRedeemed = executeMoneyMarketRedemptions(underlying, data);

    // Ensure that we have sufficient funds before we exit
    require(withdrawAmountExternal <= currentBalance.add(totalUnderlyingRedeemed)); // dev: insufficient redeem
}
```

If the currentBalance is 999,900 USDC and the withdrawAmountExternal is 1,000,000 USDC, then there is insufficient balance in the contract, and additional funds need to be withdrawn from the money market (e.g. Compound).

Since the contract already has 999,900 USDC, only an additional 100 USDC needs to be withdrawn from the money market to fulfill the withdrawal request of 1,000,000 USDC.

However, instead of withdrawing 100 USDC from the money market, Notional withdraws 1,000,000 USDC from the market as per the oracle.getRedemptionCalldata(withdrawAmountExternal) function. As a result, an excess of 990,000 USDC is being withdrawn from the money market.

This led to an excessive amount of assets idling in Notional and not generating any returns or interest in the money market, which led to a loss of assets for the users as they would receive a lower interest rate than expected and incur opportunity loss.

Attackers could potentially abuse this to pull the funds Notional invested in the money market leading to griefing and loss of returns/interest for the protocol.

## Recommendation
Consider withdrawing only the shortfall amount from the money market.

```solidity
(RedeemData[] memory data) = oracle.getRedemptionCalldata(withdrawAmountExternal - currentBalance);
```
