# [H] The settle() function can deal with a number of issues.

## Summary
Severity: High
Reporter: OCC
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175
Type: audit-issue

## Details
# The settle() function can deal with a number of issues.

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175

## Summary
There are several issues that can be addressed in the `settle()` function, _reentrancy attacks_, _the function being called multiple times_ and _the NFT being minted multiple times_ , _no fired an event when the NFT is minted_, and _no emit an event to log any errors that occur._

## Vulnerability Detail
1. It doesn't use the `nonreentrant` decorator, which can make it vulnerable to _reentrancy attacks_. 
2. It doesn't check if the auction has already been settled. For this why, the function being called multiple times and the `NFT` being minted multiple times, which is not expected. 
3. It doesn't emit an event when the `NFT` is minted . 
4. It doesn't handle errors that may occur during the execution of `MintableNFT(NFT).mint()`

## Impact
High

## Code Snippet
Manually Review

## Tool used
Manually Review

### Manual Review
Done

## Recommendation
Here is an updated version of the `settle() `function in which I tried to my best 

```solidity
@external
@nonreentrant("lock")
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
    assert self.auction_settled == False, "auction already settled"

    self.auction_settled = True

    winner: address = self.highest_bidder
    token_id: uint256 = self.current_epoch_token_id
    winning_amount: uint256 = self.highest_bid

    if winner == empty(address):
        winner = FALLBACK_RECEIVER
        log AuctionSettledWithNoBid(token_id, FALLBACK_RECEIVER)
    else:
        log AuctionSettled(token_id, winner, winning_amount)

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

    try:
        MintableNFT(NFT).mint(winner, token_id)
        if winning_amount > 0:
            ERC20(WETH).approve(self.vault, winning_amount)
            Vault(self.vault).register_deposit(token_id, winning_amount)
    except:
        log AuctionSettlementError(token_id, winner, winning_amount)

    self.auction_settled = False

```
In above, it is also necessary add a boolean value `auction_settled` to the contract state, and initialize it to `False` in the contract constructor
