# [M] Incomplete support for MATIC token

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/81
Type: sherlock-finding

## Details
WATCHPUG

medium

# Incomplete support for MATIC token

## Summary

While the current implementation deliberately handle the case of MATIC token, the support is still incomplete.

## Vulnerability Detail

When the fee token is `MATIC` (`0x0000000000000000000000000000000000001010`), the secondary swap from fee token to TEL token will most certainly fail.

As it won't be able to pull funds from the `safe`, plus, 1inch `_aggregator` also can not pull funds from the feeBuyBack contract.

## Impact

Whenever `MATIC` is used as the fee token, the transaction will fail.

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L70-L73

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L77


## Tool used

Manual Review

## Recommendation

Skip the secondary swap when the fee token is MATIC:

```diff
    //MATIC does not allow for approvals
    //ERC20s only
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/81_
