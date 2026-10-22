# [M] The auction can be started by anyone calling `settle` before `start_auction` is called by the owner

## Summary
Severity: Medium
Reporter: seyni
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L191-L193
Type: audit-issue

## Details
# The auction can be started by anyone calling `settle` before `start_auction` is called by the owner

## Summary
`settle` can be called by anyone before `start_auction` is called by the owner which lead for anyone to be able to virtually call `start_auction` as well as reducing the number of auctions by 1.

## Vulnerability Detail
Before `start_auction` is called:
- `_epoch_in_progress == False` since `epoch_end == 0`. As a consequence anyone can call the function before it as been started by the owner.
- `winner == empty(address)` since there is no `highest_bidder` yet. As a consequence, `winner` becomes `FALLBACK_RECEIVER` like so:
[AuctionHouse.vy#L191-L193](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L191-L193)
```vyper
    if winner == empty(address):
        winner = FALLBACK_RECEIVER
        log AuctionSettledWithNoBid(token_id, FALLBACK_RECEIVER)
```
- `current_epoch_token_id == 0` since no epoch have passed yet. Therefore `epoch_start` and `epoch_end` get initialized and `current_epoch_token_id` get incremented like so:

[AuctionHouse.vy#L200-L203](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L200-L203)
```vyper
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
```

A NFT will be minted to the `FALLBACK_RECEIVER`:
[AuctionHouse.vy#L208](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208)
```vyper
    MintableNFT(NFT).mint(winner, token_id)
```

But no `winning_amount` will be sent to the vault since `winning_amount == 0`

## Impact
Anyone can virtually call `start_auction` which is a permissionned function.
The number of auctions will be reduced by 1.

## Code Snippet
[AuctionHouse.vy#L174-L213](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L174-L213)
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

## Tool used

Manual Review

## Recommendation
I recommend adding a boolean value which would be turned `True` when the owner call `start_auction` and checked in the `settle function` as being `True`.
