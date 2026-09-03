# [M] `Marketplace::burn()` Logic problem

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/157
Type: sherlock-finding

## Details
8olidity

medium

# `Marketplace::burn()` Logic problem

## Summary
`Marketplace::burn()` Logic problem
## Vulnerability Detail
In `burn()` and `burnForUnderlying()` of the Marketplace, the comment says  `transfer the underlying tokens to the pool`. But the code is not the underlying token that is being sent

```solidity
Safe.transferFrom(IERC20(address(pool)), msg.sender, address(pool), a);
```

Here we should take `IERC20(pool.base())`
## Impact
`Marketplace::burn()` Logic problem
## Code Snippet
https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Marketplace.sol#L549
## Tool used

Manual Review

## Recommendation
```solidity
Safe.transferFrom(IERC20(address(pool.base())), msg.sender, address(pool), a);
```
