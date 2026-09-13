# [M] Anyone can start an auction

## Summary
Severity: Medium
Reporter: 7siech
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L247
Type: audit-issue

## Details
# Anyone can start an auction

## Summary

It is possible for anyone to call `settle` right after the `AuctionHouse` contract has been deployed causing the NFT with `_start_token_id` to be minted to the `fallback_receiver` and setting `self.epoch_start` to the current `block.timestamp` effectively starting the auction to start accepting bids without the owner ever having called `start_auction`.

## Vulnerability Detail

Both `self.epoch_start` and `self.epoch_end` have a default value of `0` and thus `_epoch_in_progress()` will evaluate to `False` fulfilling the `assert` in `settle()`.

Once `settle()` has been called, `self.epoch_start` will be set to `block.timestamp` and thus `bid()` can be called.

## Impact

- The NFT with `start_token_id` will be minted and transferred to the `fallback_receiver`
- The auction will start accepting bids

## POC

https://gist.github.com/alpeware/5da1460704f1d74461db9ddb3fa674c7#file-auctionhouse-t-sol-L177

## Code Snippet

This will evaluate to `False` right after the contract has been deployed.

```vyper
@internal
@view
# @audit q epoch start and end can be the same
def _epoch_in_progress() -> bool:
    """ 
    @notice
        Checks if we are currently between epoch_start and epoch_end.
    """
    return block.timestamp >= self.epoch_start and block.timestamp <= self.epoch_end
```
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L247

Allowing anyone to call `settle()`

```vyper
@external
def settle():
    """
    @notice
        Settles the latest epoch / auction.
        Reverts if the auction is still running.
        Mints the NFT to the highest bidder. 
        If there are no bids, mints the NFT to the FALLBACK_RECEIVER
        address.
        Resets everything and starts the next epoch / auction.
    """
    assert self._epoch_in_progress() == False, "epoch not over"
  ...
```
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175

And subsequently place a `bid`

```vyper
@external
@nonreentrant("lock")
def bid(_token_id: uint256, _amount: uint256):
    """
    @notice
        Create a new bid for _token_id with _amount.
        Requires msg.sender to have approved _amount of WETH to be transferred
        by this contract.
        If the bid is valid, the previous bidder is refunded.
        If the bid is close to epoch_end, the auction is extended to prevent 
        sniping.
    @param _token_id
        The token id a user wants to bid on.
    @param _amount
        The amount of WETH a user wants to bid.
    """
    assert self._epoch_in_progress(), "auction not in progress"
  ...
```
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133

## Tool used

Foundry
Manual Review

## Recommendation

Adding an additional assert to `settle` -

```vyper
assert self.epoch_start > 0, "auction not started"
```
