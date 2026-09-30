# [M] DOS the Auction

## Summary
Severity: Medium
Reporter: csanuragjain
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L315
Type: audit-issue

## Details
# DOS the Auction

## Summary
An Attacker can always bid higher in order to win Auction. Before the auction can be settled, attacker can simply call `refund_highest_bidder` function to refund his bid amount. This causes Auction to complete without any winner even though users were interested in this Auction

## Vulnerability Detail

1. An auction A1 is live
2. User U1,U2,U3 made bids on this Auction
3. Attacker makes the highest bid and finally wins the Auction
4. Before anyone can call `settle` function, Attacker calls `refund_highest_bidder` function which refunds the bid amount back to Attacker

```solidity
def refund_highest_bidder():
    assert msg.sender == self.owner, "unauthorized"
    assert self._epoch_in_progress() == False, "epoch not over"

    refund_amount: uint256 = self.highest_bid
    refund_receiver: address = self.highest_bidder

    self.highest_bid = 0
    self.highest_bidder = empty(address)

    ERC20(WETH).transfer(refund_receiver, refund_amount)
```

5. Thus Attacker has forced the Auction system to complete without any winner. Attacker can repeat for all upcoming auction to DOS the system

## Impact
Even when Users are interested to participate in Auction, they will fail to take part and Auction will always complete without any winner

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L315

## Tool used
Manual Review

## Recommendation
If current Auction has ended and final winner is calling `refund_highest_bidder` function then User should be refunded after taking fees
