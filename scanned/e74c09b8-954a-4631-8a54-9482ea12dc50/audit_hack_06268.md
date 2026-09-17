# [M] Front running attack in bid.

## Summary
Severity: Medium
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133-L171
Type: audit-issue

## Details
# Front running attack in bid.

## Summary
The bad actor can monitor the transactions in the mempool, once he finds some one want to create a new bid  he can front run to block new user to create it.

## Vulnerability Detail
```vyper
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

    assert _amount >= RESERVE_PRICE, "reserve price not met"
    assert _token_id == self.current_epoch_token_id, "token id not up for auction"
    assert _amount > self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100 , "bid not high enough" 

    last_bidder: address = self.highest_bidder
    last_bid: uint256 = self.highest_bid

    self.highest_bid = _amount
    self.highest_bidder = msg.sender

    # extend epoch_end to avoid sniping if necessary
    if block.timestamp > self.epoch_end - TIME_BUFFER:
        self.epoch_end = block.timestamp + TIME_BUFFER
        log AuctionExtended(_token_id, self.epoch_end)

    # refund last bidder
    if last_bidder != empty(address) and last_bid > 0:
        ERC20(WETH).transfer(last_bidder, last_bid)
        log BidRefunded(_token_id, last_bidder, last_bid)

    # collect bid from current bidder
    ERC20(WETH).transferFrom(msg.sender, self, _amount)
    log Bid(_token_id, self.highest_bidder, self.highest_bid)

```
The ```bid()``` function is used to create a new bid for ```_token_id with _amount``` if the amount specified in the parametersis greater than ```self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100```.It can be front runed to block new users from creating a new bid.
1.Alice create a new bid.
2. She  monitors the transactions in the mempool, once she finds some one want to create a new bid, she front runs  with more gas  to create a new bid , setting the number of amount in the parameters to 1 more than the amount of the pending transaction parameters in the mempool.
3. Users will not able to create a new bid.

## Impact

It can be front runed to block new users from creating bid.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133-L171

## Tool used

Manual Review

## Recommendation
