# [H] `uTokens[]` upgrade could lock users fund

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/106
Type: sherlock-finding

## Details
__141345__

high

# `uTokens[]` upgrade could lock users fund

## Summary

`uToken` is upgradable, if the address of existing uToken is changed in the registry, the `balances[][]` accounting will be wrong, hence users fund could get locked and cannot be withdrawn. 


## Vulnerability Detail

`uTokens[token]` could be changed in MarketRegistry, then the previous tToken address will be treated as normal users.
Users could fail to `redeem()` from the previous uToken. Because it calls the `AssetManager.withdraw()`, and the `_checkSenderBalance()` will return false and revert.

Some of the previous uToken functions can still be called, like `mint()`. If mistakenly `mint()` and deposited into the assetManager, the fund could be stolen by other users by calling `redeem()`. Because in this case, the balance of the uToken will be positive.


## Impact

- `balances[][]` accounting will be inaccurate, `_checkSenderBalance()` will return wrong results
- users fund being locked
- some users fund could be stolen


## Code Snippet

`uTokens[token]` could be changed:
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/MarketRegistry.sol#L79-L82

The previous uToken will be treated as normal user. 
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/asset/AssetManager.sol#L560-L562

`_checkSenderBalance()` will execute the wrong logic.
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/asset/AssetManager.sol#L547-L558

## Tool used

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/106_
