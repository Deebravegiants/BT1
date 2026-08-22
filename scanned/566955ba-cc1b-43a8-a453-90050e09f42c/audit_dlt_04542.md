# [H] [WP-H3] `StableCurveEthOracle#getPrice()` Misconfiguration of Curve lp_token's oracle (mismatch the `N_COINS`) can result in wrong price

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-sentiment
Published: 2022-12-02
Source: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/17
Type: sherlock-finding

## Details
WATCHPUG

high

# [WP-H3] `StableCurveEthOracle#getPrice()` Misconfiguration of Curve lp_token's oracle (mismatch the `N_COINS`) can result in wrong price

## Summary

When a future Curve lp_token with `3` coins gets wrongfully configured to an instance of `StableCurveEthOracle.sol` with the `N_COINS` set to `2`, the result of `StableCurveEthOracle#getPrice()` can be wrong.

## Vulnerability Detail

`StableCurveEthOracle` will be deployed with a configuration of `N_COINS`, which specifies the number of coins the oracle is supposed to be used for.

However, when the `N_COINS` of the oracle contract mismatch with the number of coins of the curve pool the lp_token represents, it can still go through and usually returns a very close result.

Only if one of the tokens is depeg, for example, when a lp_token with `3` coins is using an oracle contract with `N_COINS` set to `2`, and the 3rd coin is the depeg token, then the result will be wrong by a lot.

## Impact

A wrongly configured oracle can cause a severe impact on the protocol.

In this case, because of the fact that in normal circumstances a wrongly configured oracle will not be noticeable from the result of the price.

But when the market condition changes, the wrongly configured oracle can then suddenly bring down the whole protocol.

## Code Snippet

https://github.com/sentimentxyz/oracle/blob/40cfd1e95a531e4c88e082e651efae7fc16cdefa/src/curve/StableCurveEthOracle.sol#L50

## Tool used

Manual Review

## Recommendation

Consider adding a new method to `IOracle` called `sanityCheck(address token)`, and call it in `core/OracleFacade.sol#setOracle()` to avoid any misconfiguration of oracle <> token.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/17_
