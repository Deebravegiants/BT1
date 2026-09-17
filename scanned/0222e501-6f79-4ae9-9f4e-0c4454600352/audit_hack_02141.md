# [M] `TokenToLock` default value

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

cmichel


# Vulnerability details

The `PoolBase.TokenToLockXRate` function returns the "Current exchange rate from `_token` to lockToken".

It does not specify the precision and according to the documentation, it sounds like one just has to multiply this value by any `_token` amount to get the corresponding `lockToken` amount.
Lock tokens are always in 18 decimals (as is their initial mint) but `_token` does not have to be.
The return value `TokenToLock(10**18, _token) = totalLock * 1e18 / balance` has the wrong precision, it should return `TokenToLock(10**(_token.decimals()), _token)` instead returning the lock amount per "1.0" `_token`.
