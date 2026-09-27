# [M] `start_auction` can be called after end of auction

## Summary
Severity: Medium
Reporter: carrot
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L200-L206
Type: audit-issue

## Details
# `start_auction` can be called after end of auction

## Summary
At the end of the auction, the `settle` function resets the start and end timestamps to 0. The owner can call `settle` function on this contract again by mistake, and allow it to accept bids and WETH.
## Vulnerability Detail
The function `settle` resets the timestamps when the auction ends, i.e. all tokenIds have been minted, through the following lines
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L200-L206

When the timestamps are set to 0, it makes the function `start_auction` eligible to be called again since it passes the timestamp check.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L229-L230
 This will in turn lead to the contract accepting bids and WETH, but being unable to process them properly.
## Impact
Unintended behavior of contract. Stuck/lost WETH in auctions
## Code Snippet
This can be recreated with the following POC
```python
def test_ATTACK_restart_dead_auctions(owner, house, nft):
    token_id = house.current_epoch_token_id()
    house.start_auction(0)
    timetravel(house.epoch_end() + 1)
    house.settle()
    timetravel(house.epoch_end() + 1)
    house.settle()
    assert house.epoch_end() == 0
    # Auction has ended!

    # Start again!
    house.start_auction(0)
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
    assert house.highest_bidder() == owner
```
## Tool used
Boa
Manual Review

## Recommendation
Create a flag forcing `start_auction` to run only once
```vyper
assert self.startFlag == 1, "Cant restart auction"
self.startFlag = 1
```
