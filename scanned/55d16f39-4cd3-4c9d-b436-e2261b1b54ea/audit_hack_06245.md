# [H] Anyone can mint the first token and start the auction

## Summary
Severity: High
Reporter: HonorLt
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L185
Type: audit-issue

## Details
# Anyone can mint the first token and start the auction

## Summary

Auction settling does not check if the auction has started making it possible to mint the first token and start the token for anyone.

## Vulnerability Detail

When the auction contract is deployed, an owner has to call the `start_auction` function to schedule the beginning.

However, `settle` function only checks that the epoch is not in progress:
```vyper
@external
def settle():
    ...
    assert self._epoch_in_progress() == False, "epoch not over"
```

The epoch is considered in progress when the current timestamp is between the start and end boundaries:
```vyper
@internal
@view
def _epoch_in_progress() -> bool:
    """
    @notice
        Checks if we are currently between epoch_start and epoch_end.
    """
    return block.timestamp >= self.epoch_start and block.timestamp <= self.epoch_end
```

When initially the auction is not started, the `epoch_start` and `epoch_end` are 0 by default.
This makes this condition return false and thus satisfies the requirement.

Thus once the contract is deployed anyone can bypass the owner's start by calling the `settle` function to mint the first token to the `FALLBACK_RECEIVER` and automatically start the auction for the next token id.

## Impact

It is possible to escape initial start restrictions and also mint the first token to the fallback receiver without an actual auction happening.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L185

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L245-L252

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L216-L242

## Tool used

Manual Review

## Recommendation
`settle` could check that the auction was started, e.g. `self.epoch_start > 0`.
