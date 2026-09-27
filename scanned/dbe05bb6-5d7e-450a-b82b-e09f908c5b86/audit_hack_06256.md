# [M] Extending auction can be abused to prevent auction ending for a long period

## Summary
Severity: Medium
Reporter: ck
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L159-L162
Type: audit-issue

## Details
# Extending auction can be abused to prevent auction ending for a long period

## Summary

Extending auction can be abused to prevent auction ending for a long period

## Vulnerability Detail

An auction is extended if a bid is placed when epoch is less than 15 minutes from ending:

```solidity
    # extend epoch_end to avoid sniping if necessary
    if block.timestamp > self.epoch_end - TIME_BUFFER:
        self.epoch_end = block.timestamp + TIME_BUFFER
        log AuctionExtended(_token_id, self.epoch_end)
```

A malicious bidder or group of malicious bidders can abuse this to prevent the auction from ending for a long period by continuously increasing their bid by small amounts when the `epoch_end` is within 15 minutes.

## Impact

Denial of service for an extended period.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L159-L162

## Tool used

Manual Review

## Recommendation

Consider not allowing the `epoch_end` to be extended.
