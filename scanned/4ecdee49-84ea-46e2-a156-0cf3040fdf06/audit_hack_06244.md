# [M] Any user can call settle before auction in order to mint all tokens to FALLBACK_RECEIVER and ddos AuctionHouse

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L174-L213
Type: audit-issue

## Details
# Any user can call settle before auction in order to mint all tokens to FALLBACK_RECEIVER and ddos AuctionHouse

## Summary
Any user can call settle before auction in order to mint all tokens to FALLBACK_RECEIVER and ddos AuctionHouse.
## Vulnerability Detail
Auction settle function in order to deposit funds, paid for current token to the vault and start new epoch.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L174-L213
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

First it checks, if `_epoch_in_progress` and then starts new epoch if needed, then mint nft and calls `register_deposit` for the winner.
This is how `_epoch_in_progress` is checked.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L252
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
In case when `start_auction` is not called yet, it will return false.

Attacker can call this function when auction is not started yet in order to mint all nft to the `FALLBACK_RECEIVER` and prevent bidding.

Example.
1.AuctionHouse deployed for tokens from 1 to 5.
2.Attacker calls `settle` several times before `start_auction` is called.
3.Every time nft is minted to `FALLBACK_RECEIVER` and deposit is not made as amount is 0.
4.Attacker do that until all nft (from 1 to 5) are minted.
## Impact
Attacker can ddos AuctionHouse.
## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
Do not allow to call `settle` if `epoch_start` and `epoch_end` equal to 0.
