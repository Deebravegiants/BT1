# [M] `settle` can be called after the end of all auctions

## Summary
Severity: Medium
Reporter: seyni
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L200-L206
Type: audit-issue

## Details
# `settle` can be called after the end of all auctions

## Summary
`settle` can be called after the end of all auctions which leads to an additional NFT to be minted to the `FALLBACK_RECEIVER`.

## Vulnerability Detail
When the last auctions ends, `current_epoch_token_id == max_token_id`. Thus, the else statement of this code get executed:
[AuctionHouse.vy#L200-L206](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L200-L206)
```vyper
    if self.current_epoch_token_id < self.max_token_id:
        self.current_epoch_token_id += 1
        self.epoch_start = block.timestamp
        self.epoch_end = self.epoch_start + EPOCH_LENGTH
    else:
        self.epoch_start = 0
        self.epoch_end = 0
```
Since `self.epoch_end == 0`, `_epoch_in_progress() == False` which means that `settle` can be called.
A call to `settle` at this point will mint an additional NFT to `FALLBACK_RECEIVER` with `token_id == max_token_id`.

## Impact
An additionnal NFT is minted to `FALLBACK_RECEIVER`.

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
I recommend turning `False` a boolean which would have been turned `True` when the owner called `start_auction`, in the following else statement:
[AuctionHouse.vy#L204-L206](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L204-L206)
```vyper
    else:
        self.epoch_start = 0
        self.epoch_end = 0
+       auctionStarted = False
```
The boolean will need to be checked as being `True` during the auctions in `settle`.
