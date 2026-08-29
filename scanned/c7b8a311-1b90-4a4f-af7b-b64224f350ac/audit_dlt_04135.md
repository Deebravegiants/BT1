# [M] `AuctionHouse.createBid()` emits an `AuctionDurationExtended` event wrongly.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/226
Type: sherlock-finding

## Details
hansfriese

medium

# `AuctionHouse.createBid()` emits an `AuctionDurationExtended` event wrongly.

## Summary
`AuctionHouse.createBid()` emits an `AuctionDurationExtended` event wrongly.

## Vulnerability Detail
`AuctionHouse.createBid()` emits an `AuctionDurationExtended` event when the auction duration is extended.

It tries to extend the duration when the difference is less than the `timeBuffer` [here](https://github.com/sherlock-audit/2022-10-astaria/blob/main/lib/astaria-gpl/src/AuctionHouse.sol#L127-L146).

```solidity
    if (firstBidTime + duration - block.timestamp < timeBuffer) {
      // Playing code golf for gas optimization:
      // uint256 expectedEnd = auctions[auctionId].firstBidTime.add(auctions[auctionId].duration);
      // uint256 timeRemaining = expectedEnd.sub(block.timestamp);
      // uint256 timeToAdd = timeBuffer.sub(timeRemaining);
      // uint256 newDuration = auctions[auctionId].duration.add(timeToAdd);

      //TODO: add the cap to the duration, do not let it extend beyond 24 hours extra from max duration
      uint64 newDuration = uint256(
        duration + (block.timestamp + timeBuffer - firstBidTime)
      ).safeCastTo64();
      if (newDuration <= auctions[tokenId].maxDuration) {
        auctions[tokenId].duration = newDuration;
      } else {
        auctions[tokenId].duration =
          auctions[tokenId].maxDuration -
          firstBidTime;
      }
      extended = true;
    }
```

According to the current implementation, it doesn't extend the duration if it reaches the `maxDuration`.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/226_
