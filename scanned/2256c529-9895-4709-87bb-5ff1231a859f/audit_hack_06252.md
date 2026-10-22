# [M] A Malicious User Can Front-runned And Settels First Auction Even Before Bidding Starts For It.

## Summary
Severity: Medium
Reporter: 0xhacksmithh
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L185
Type: audit-issue

## Details
# A Malicious User Can Front-runned And Settels First Auction Even Before Bidding Starts For It.

## Summary
Owner can be front-runed or If Owner set auction start time i.e ```epoch_start``` in near future then User can Settle First Auction Even before Its Bidding Begins

## Vulnerability Detail
```settle()``` used for Settling the latest epoch / auction and Reverts if the auction is still running. To check that it has following assert condition 
```solidity
assert self._epoch_in_progress() == False, "epoch not over"
```
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L185
```solidity
@internal
@view
def _epoch_in_progress() -> bool:
    """
    @notice
        Checks if we are currently between epoch_start and epoch_end.
    """
    return block.timestamp >= self.epoch_start and block.timestamp <= self.epoch_end

```
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L247-L252

Let for instance assume Contract get deployed and Owner didn't call ```start_auction()```(or may be he front-runned)
So at that time, both ``` self.epoch_start``` and ``` self.epoch_end``` are 0, and ```_epoch_in_progress()``` will return ```false``` 

So checks on ```settle()``` function get satisfied and it will settle first auction means it mints the NFT to the ```FALLBACK_RECEIVER``` address. Resets everything and starts the next epoch / auction.
```solidity
# set up next round if there is one
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
    else:
        self.epoch_start = 0
        self.epoch_end = 0
```
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L213

This Issue also remain same when Owner deploy contracts and call ```start_auction()``` Successfully but he set ``` self.epoch_start``` in near future i.e greater that current ```block.timestamp```
At that time ```_epoch_in_progress()``` will also returns ```false``` as ```block.timestamp < self.epoch_start```

So during this time any User can Settle that First Auction even before Bidding start



```solidity
@external
def settle(): // @audit Can be front runned should have access control for first one
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

    winner: address = self.highest_bidder
    token_id: uint256 = self.current_epoch_token_id
    winning_amount: uint256 = self.highest_bid

    if winner == empty(address):
        winner = FALLBACK_RECEIVER
        log AuctionSettledWithNoBid(token_id, FALLBACK_RECEIVER)

    # reset for next round
    self.highest_bid = 0
    self.highest_bidder = empty(address)

    # set up next round if there is one
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
    else:
        self.epoch_start = 0
        self.epoch_end = 0

    MintableNFT(NFT).mint(winner, token_id)

    if winning_amount > 0:
        ERC20(WETH).approve(self.vault, winning_amount)
        Vault(self.vault).register_deposit(token_id, winning_amount)
        log AuctionSettled(token_id, winner, winning_amount)
```

## Impact
When Contract deployed or Auction starts First Auction will Settled by Malicious User before even its Bidding start.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L247-L252
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L213
## Tool used

Manual Review

## Recommendation
Should make some logic change.
May be call ```start_auction()``` during contract Initialization time and set ```epoch_start``` to ```block.timestamp```
