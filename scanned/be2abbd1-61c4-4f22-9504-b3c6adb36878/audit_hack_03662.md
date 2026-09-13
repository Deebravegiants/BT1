# [M] Unsafe ERC20 methods

## Summary
Severity: Medium
Reporter: WATCHPUG
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97
Type: audit-issue

## Details
# Unsafe ERC20 methods

## Summary

Using unsafe ERC20 methods can revert the transaction for certain tokens.

## Vulnerability Detail

There are many [Weird ERC20 Tokens](https://www.hacknote.co/17c261f7d8fWbdml/doc/182a568ab5cUOpDM) that won't work correctly using the standard `IERC20` interface.

For example, `IERC20(token).transferFrom()` and `IERC20(token).transfer()` will fail for some tokens as they may not conform to the standard IERC20 interface. And if `_aggregator` does not always consume all the allowance given at L72, the transaction will also revert on the next call, because there are certain tokens that do not allow approval of a non-zero number when the current allowance is not zero (eg, USDT).

## Impact

The contract will malfunction for certain tokens.

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L47-L82

## Tool used

Manual Review

## Recommendation

Consider using `SafeERC20` for `transferFrom`, `transfer` and `approve`.
