# [H] Auction can be started without previous one being settled

## Summary
Severity: High
Reporter: ck
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L217-L242
Type: audit-issue

## Details
# Auction can be started without previous one being settled

## Summary

Auction can be started without previous one being settled

## Vulnerability Detail

Starting a new auction uisng the `start_auction` function does not check whether the previous auction has been settled:

```solidity
    # epoch_start has already been set and is in the past
    if self.epoch_start != 0 and self.epoch_start <= block.timestamp: 
        raise "auction already started"
```

So if an auction has ended and not been settled, a new one could be started with stale values of `highest_bid`, `highest_bidder` and `current_epoch_token_id`.

## Impact

A new auction can be started that would break intended epoch and bidding functionality.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L217-L242

## Tool used

Manual Review

## Recommendation

Add a check to determine if there is an auction that has not been settled and revert if an attempt to start an auction is done.
