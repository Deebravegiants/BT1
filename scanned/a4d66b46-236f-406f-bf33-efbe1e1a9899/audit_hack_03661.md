# [M] `transfer()` and `transferFrom()` should not be used when interacting with arbitrary ERC20 tokens

## Summary
Severity: Medium
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97
Type: audit-issue

## Details
# `transfer()` and `transferFrom()` should not be used when interacting with arbitrary ERC20 tokens

## Summary
OpenZeppelin recommends to always use `safeTransfer()` and `safeTransferFrom()` due to the various implementation of ERC20 tokens that may not fully comply with the token standard, such as those returning a `false` instead of reverting in case of failure.

## Vulnerability Detail
`transfer()` and `transferFrom()` is used in when doing a secondary swap in `submit()` as well as in `rescueERC20()`. This is an issue since all ERC20 tokens are allowed.

## Impact

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L70-L73

## Tool used

Manual Review

## Recommendation
Use OpenZeppelin's implementation of `safeTransfer()` and `safeTransferFrom()` that covers weird ERC20 tokens.
