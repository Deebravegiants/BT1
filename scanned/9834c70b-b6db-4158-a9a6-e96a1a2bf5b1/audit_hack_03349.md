# [H] ERC777 tokens can do advantageous swaps by reentering swap functions

## Summary
Severity: High
Reporter: koxuan
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L229
Type: audit-issue

## Details
# ERC777 tokens can do advantageous swaps by reentering swap functions

## Summary
When ERC777 token is used as from Token, a user can reenter `dodoMutliSwap`, `mixSwap` and `externalSwap`, which enables swaps to be done before liquidity pool values are updated.  

## Vulnerability Detail
As `dodoMutliSwap`, `mixSwap` and `externalSwap` is not reentrancy guarded, it relies on the adapter to make sure that the reentrancy guard is done to prevent erc777 from reentering and swapping tokens before the amount in the liquidity pool is updated.  

## Impact
User can swap without liquidity pool calculation changing accordingly to the token being added into the liquidity pool.

## Code Snippet
[DODORouteProxy#L164-L229](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L229)
[DODORouteProxy#L238-L311](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L238-L311)
[DODORouteProxy#L323-L383](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L323-L383)


## Tool used

Manual Review

## Recommendation
Add  reentrancy guards for all the swap functions.
