# [M] `refund_highest_bidder` can be frontrun by a call to `settle`

## Summary
Severity: Medium
Reporter: seyni
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L315-L325
Type: audit-issue

## Details
# `refund_highest_bidder` can be frontrun by a call to `settle`

## Summary
Anyone can frontrun the owner calling `refund_highest_bidder` by calling `settle` which leads for the owner to potentially not be able to call the function for any `highest_bidder` of auctions.

## Vulnerability Detail
Anyone can call `settle` as soon as the current auction ends. As a consequence, any call to `refund_highest_bidder` by the owner can be frontrun by a call to `settle` which will start the next auction and set `_epoch_in_progress()` to `True` and set `highest_bidder` to `empty(address)`.

## Impact
The owner will potentially not be able to call `refund_highest_bidder` for any `highest_bidder` of auctions.

## Code Snippet
[AuctionHouse.vy#L315-L325](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L315-L325)
```vyper
def refund_highest_bidder():
    assert msg.sender == self.owner, "unauthorized"
    assert self._epoch_in_progress() == False, "epoch not over"


    refund_amount: uint256 = self.highest_bid
    refund_receiver: address = self.highest_bidder


    self.highest_bid = 0
    self.highest_bidder = empty(address)


    ERC20(WETH).transfer(refund_receiver, refund_amount)
```

## Tool used

Manual Review

## Recommendation
I recommend making `settle` only callable by the owner or a permissionned role.
