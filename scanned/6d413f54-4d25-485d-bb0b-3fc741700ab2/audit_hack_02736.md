# [M] Inconsistent condition to finalize the auction.

## Summary
Severity: Medium
Reporter: hansfriese
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L557
Type: audit-issue

## Details
# Inconsistent condition to finalize the auction.

## Summary
Inconsistent condition to finalize the auction.

## Vulnerability Detail
Inconsistent condition to finalize the auction.

When we try to finalize the aunction [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L557) and [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L222), we check if `block.timestamp >= auction.startTime`.

```solidity
if (block.timestamp >= auction.startTime) {
    _finalizeAuction(l, auction, epoch);
}
```

But [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L343), it checks if `block.timestamp > auction.startTime`.

```solidity
} else if (
    block.timestamp > auction.startTime &&
    auction.status == AuctionStorage.Status.INITIALIZED
) {
```

## Impact
The same `finalization` logic will be applied with different condition.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L343

## Tool used
Manual Review

## Recommendation
We should change `>` to `>=` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L343).

```solidity
} else if (
    block.timestamp >= auction.startTime && 
    auction.status == AuctionStorage.Status.INITIALIZED
) {
    // finalize the auction only if the auction has started
    _finalizeAuction(l, auction, epoch);
}
```
