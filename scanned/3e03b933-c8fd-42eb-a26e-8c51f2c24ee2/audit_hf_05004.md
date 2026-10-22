# [H] Compound v2 Empty Markets Exploit.

## Summary
Severity: High
Contest weight: 0.6225
Dataset id: 22993
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deepr protocol, being a fork of Compound v2, is vulnerable to the empty markets exploit. This vulnerability allows an attacker to drain the entire protocol if there is a market with zero liquidity and a non-zero collateral factor. The root cause of the attack is a rounding issue in the redeemUnderlying function. Whenever a user redeems their underlying tokens (WBTC in this case), the number of shares to burn is calculated as follows:
shares to burn = underlying token amount / exchangeRate
But instead of rounding up, the number of shares to burn is rounded down in redeemUnderlying function. Due to this, in some cases, one wei fewer number of shares will be burned. The attacker can amplify this rounding by inflating the exchangeRate of the empty market.

```solidity
function redeemFresh(address payable redeemer, uint redeemTokensIn, uint redeemAmountIn) internal {
    require(redeemTokensIn == 0 || redeemAmountIn == 0, "one of redeemTokensIn or redeemAmountIn must be zero");
    Exp memory exchangeRate = Exp({mantissa: exchangeRateStoredInternal() });
    uint redeemTokens;
    uint redeemAmount;
    if (redeemTokensIn > 0) {
        redeemTokens = redeemTokensIn;
        redeemAmount = mul_ScalarTruncate(exchangeRate, redeemTokensIn);
    } else {
        redeemTokens = div_(redeemAmountIn, exchangeRate);
        redeemAmount = redeemAmountIn;
    }
    totalSupply = totalSupply - redeemTokens;
    accountTokens[redeemer] = accountTokens[redeemer] - redeemTokens;
    ...
}
```
Attack Steps: More about the attack steps: here
An attacker can drain the whole protocol if there is a market with non-zero collateral-factor and zero liquidity

## Recommendation
• Ensure that markets never reach a zero liquidity state by minting a small amount of shares and sending them to the zero address.
• When listing a new collateral token, first set its collateral factor to zero, then mint some shares, send them to the zero address, then change the collateral factor to the desired value.
