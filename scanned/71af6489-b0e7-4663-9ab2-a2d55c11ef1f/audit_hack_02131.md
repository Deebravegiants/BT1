# [M] `YieldSourcePrizePool_canAwardExternal` does not work

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

cmichel


# Vulnerability details

The idea of `YieldSourcePrizePool_canAwardExternal` seems to be to disallow awarding the interest-bearing token of the yield source, like aTokens, cTokens, yTokens.

> "@dev Different yield sources will hold the deposits as another kind of token: such a Compound's cToken.  The prize strategy should not be allowed to move those tokens."

However, the code checks `_externalToken != address(yieldSource)` where `yieldSource` is the actual yield strategy contract and not the strategy's interest-bearing token.
Note that the `yieldSource` is usually not even a token contract except for `ATokenYieldSource` and `YearnV2YieldSource`.

## Impact

The `_canAwardExternal` does not work as expected.
It might be possible to award the interest-bearing token which would lead to errors and loss of funds when trying to redeem underlying.

## Recommended Mitigation Steps

There doesn't seem to be a function to return the interest-bearing token. It needs to be added, similar to `depositToken()` which retrieves the underlying token.
