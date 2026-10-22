# [H] Potential reentrancy attack vulnerability in in the 'bid' function

## Summary
Severity: High
Reporter: OCC
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133
Type: audit-issue

## Details
# Potential reentrancy attack vulnerability in in the 'bid' function

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133

## Summary
I think the `bid` function seems to be vulnerable to a _reentrancy attack_, although it uses the `nonreentrant` decorator but does not include any explicit state updates that would block _reentrancy_.

## Vulnerability Detail
The `bid `function only uses the `nonreentrant` decorator to prevent  _reentrancy attacks_  but does not contain any explicit state updates that would prevent _reentrancy_. By repeatedly invoking the `bid` function from a malicious contract, someone could be able to take advantage of the vulnerability and run extra code while the `bid` function is still running.

## Impact
High

## Code Snippet
Manually Review

## Tool used
Manually Review

### Manual Review
Done

## Recommendation
Here's an updated version of the `bid `function that includes an additional state change to prevent reentrancy attacks:

```solidity
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

      
    # Add explicit state change to prevent reentrancy
        self.highest_bid = self.highest_bid


    # refund last bidder
    if last_bidder != empty(address) and last_bid > 0:
        self.highest_bidder = empty(address)            # clear bidder to prevent reentrant call
        ERC20(WETH).transfer(last_bidder, last_bid)
        log BidRefunded(_token_id, last_bidder, last_bid)

    # collect bid from current bidder
    ERC20(WETH).transferFrom(msg.sender, self, _amount)
    log Bid(_token_id, self.highest_bidder, self.highest_bid)

```
In the above, add a line that sets the `self.highest_bid `to its current value, which is an explicit state change that prevents `reentrancy attacks`. And we can also add a line that clears the `self.highest_bidder` if we need to refund the previous bidder, which ensures that subsequent calls to the function from that bidder will be rejected.
