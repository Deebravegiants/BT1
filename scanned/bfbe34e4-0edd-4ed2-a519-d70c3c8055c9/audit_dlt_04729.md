# [H] `OrderBook._remove()` doesn't update `index.length` properly.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/144
Type: sherlock-finding

## Details
hansfriese

medium

# `OrderBook._remove()` doesn't update `index.length` properly.

## Summary
`OrderBook._remove()` doesn't update `index.length` properly.

## Vulnerability Detail
`OrderBook._remove()` doesn't update `index.length` properly.

[OrderBook._remove()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/OrderBook.sol#L240) is used to remove the existing order from the tree and `index.length` should be 0 when the original tree is empty.

```solidity
index.length = index.length > 0 ? index.length - 1 : 1;
```

## Impact
`OrderBook._remove()` updates `index.length` wrongly and [_length()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/OrderBook.sol#L41) will return the wrong result.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/OrderBook.sol#L240

## Tool used
Manual Review

## Recommendation
We should change [this line](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/OrderBook.sol#L240) like below.

```solidity
index.length = index.length > 0 ? index.length - 1 : 0;
```
