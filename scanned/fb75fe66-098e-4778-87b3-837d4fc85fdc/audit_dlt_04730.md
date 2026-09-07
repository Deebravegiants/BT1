# [M] `Auction.getEpochsByBuyer()` might omit some valid epochs.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/143
Type: sherlock-finding

## Details
hansfriese

medium

# `Auction.getEpochsByBuyer()` might omit some valid epochs.

## Summary
`Auction.getEpochsByBuyer()` might omit some valid epochs.

## Vulnerability Detail
`Auction.getEpochsByBuyer()` might omit some valid epochs.

Currently, `epochsByBuyer` is saved using `UintSet` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionStorage.sol#L65), and the epoch will be saved only once even if the buyer added several orders on the same epoch.

So the below scenario would be possible.
- The buyer added 2 limit orders on the same epoch using `addLimitOrder()`.
- The `epochsByBuyer` will contain the epoch [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L553).
- After that, the buyer removed one limit order and another one is still active.
- But the epoch will be removed from `epochsByBuyer` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L220) and [getEpochsByBuyer()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L429) won't return the epoch even though the buyer has one limit order.

## Impact
`Auction.getEpochsByBuyer()` might output less epochs than it should.

## Code Snippet
- https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L429
- https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L220

## Tool used
Manual Review

## Recommendation
I think we should use mapping instead of `UintSet` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionStorage.sol#L65) to track the total number of active orders for each buyer.

Then `Auction.getEpochsByBuyer()` can output the epochs that contain at least one active order.


Duplicate of #86
