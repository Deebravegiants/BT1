# [M] Auction for one side restricts users on the other side as well

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/195
Type: sherlock-finding

## Details
hansfriese

medium

# Auction for one side restricts users on the other side as well

## Summary

The protocol has two independent auctions for depositors and withdrawers. While these are completely independent, they are controlled by a single variable `isAuctionLive` and an auction for one side restricts users on the other side from dequeing their requests unnecessarily.

## Vulnerability Detail

There is a single flag `isAuctionLive` which is set to True by the admin on the start of auction.

```solidity
function toggleAuctionLive() external onlyOwner {
    isAuctionLive = !isAuctionLive;
    emit ToggledAuctionLive(isAuctionLive);
}
```

And whenever this variable is set to True, users are not allowed to deque their requests.

```solidity
// #278
function withdrawUSDC(uint256 _amount) external {
    require(!isAuctionLive, "auction is live");
    ...
}
...
// #323
function dequeueCrab(uint256 _amount) external {
    require(!isAuctionLive, "auction is live");
    ...
}

```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/195_
