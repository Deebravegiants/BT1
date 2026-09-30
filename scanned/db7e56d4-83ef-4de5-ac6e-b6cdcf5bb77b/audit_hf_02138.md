# [M] Empty Market Avoidance With MINIMUM_LIQUIDITY Enforcement

## Summary
Severity: Medium
Contest weight: 0.4653
Dataset id: 11997
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Enzo protocol is in essence an over-collateralized lending pool that has the lending functionality and supports a number of normal lending functionalities for supplying and borrowing users, i.e., public mint()/redeem() and borrow()/repay(). While reviewing the redeem logic, we notice the current implementation has a precision issue that has been reflected in a recent HundredFinance hack. To elaborate, we show below the related redeemFresh() routine. As the name indicates, this routine is designed to redeem CTokens in exchange for the underlying asset. When the user indicates the underlying asset amount (via redeemUnderlying()), the respective redeemTokens is computed as redeemTokens = div_(redeemAmountIn, exchangeRate) (line 639). Unfortunately, the current approach may unintentionally introduce a precision issue by computing the redeemTokens amount against the protocol. Specifically, the resulting flooring-based division introduces a precision loss, which may be just a small number but plays a critical role when certain boundary conditions are met as demonstrated in the recent HundredFinance hack: https://blog.hundred.finance/15-04-23-hundred-finance-hack-post-mortem-d895b618cf33.
```solidity
function redeemFresh(address payable redeemer, uint redeemTokensIn, uint redeemAmountIn) internal returns (uint) {
    require(redeemTokensIn == 0 || redeemAmountIn == 0, "zero");
    RedeemLocalVars memory vars;
    // exchangeRate = invokeExchangeRateStored()
    vars.exchangeRateMantissa = exchangeRateStoredInternal();
    /* If redeemTokensIn > 0: */
    if (redeemTokensIn > 0) {
        // We calculate the exchange rate and the amount of underlying to be redeemed:
        // redeemTokens = redeemTokensIn
        // redeemAmount = redeemTokensIn x exchangeRateCurrent
        vars.redeemTokens = redeemTokensIn;
        vars.redeemAmount = mul_ScalarTruncate(Exp({mantissa: vars.exchangeRateMantissa}), redeemTokensIn);
    } else {
        // We get the current exchange rate and calculate the amount to be redeemed:
        // redeemTokens = redeemAmountIn / exchangeRate
        // redeemAmount = redeemAmountIn
        vars.redeemTokens = div_ScalarByExpTruncate(redeemAmountIn, Exp({mantissa: vars.exchangeRateMantissa}));
        vars.redeemAmount = redeemAmountIn;
    }
    /* Fail if redeem not allowed */
    uint allowed = comptroller.redeemAllowed(address(this), redeemer, vars.redeemTokens);
    if (allowed != 0) {
        return failOpaque(Error.COMPTROLLER_REJECTION, FailureInfo.REDEEM_COMPTROLLER_REJECTION, allowed);
    }
}
```

## Recommendation
Properly revise the above routine to ensure the precision loss needs to be computed in favor of the protocol, instead of the user. In particular, we need to ensure that markets are never empty by minting small CToken balances at the time of market creation so that we can prevent the rounding error being used maliciously. A deposit as small as 1 wei is sufficient.
