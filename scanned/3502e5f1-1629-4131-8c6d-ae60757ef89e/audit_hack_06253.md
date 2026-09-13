# [M] Anyone can start the auction

## Summary
Severity: Medium
Reporter: Bahurum
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L202
Type: audit-issue

## Details
# Anyone can start the auction

## Summary
Anyone can start the auction by calling `AuctionHouse.settle()` before the actual start time set. also, initial NFT will be minted to the fallback receiver. Fix: 

## Vulnerability Detail
If `start_auction()` has not been called yest or it has been called with `_start_time` in the future, then it is possible to call `settle()` and start the auction. 

- Anyone calls settle()
- `self._epoch_in_progress() == False` since either `block.timestamp < self.epoch_start` or `self.epoch_end == 0` so execution of `settle()` continues
- at line [202](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L202) condition is true and `self.epoch_end` is set to current timestamp.
- Initial NFT is minted to `FALLBACK_RECEIVER`
- It is now possible to make the first bid

## Impact
Deployer has no control over when auction goes live, and it can be started by anyone after the Auction House is deployed. This will throw off the timeline scheduled for the mint by the protocol team.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L185

## Tool used

Manual Review

## Recommendation
Add `assert self.epoch_end  > 0` as an additional check at the beginning of `settle()`
