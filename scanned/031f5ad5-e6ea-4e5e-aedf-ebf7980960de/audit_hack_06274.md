# [M] Attacker can front-run `AuctionHouse.refund_highest_bidder` to block refunding

## Summary
Severity: Medium
Reporter: XKET
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L212
Type: audit-issue

## Details
# Attacker can front-run `AuctionHouse.refund_highest_bidder` to block refunding



## Summary
Attacker can front-run `refund_highest_bidder` to block refunding in `AuctionHouse`.

## Vulnerability Detail

`AuctionHouse.settle` can be failed when it interacts with Vault.

```vyper
    Vault(self.vault).register_deposit(token_id, winning_amount)
```

In this case, the highest bidder's fund is locked in the auction house, so the owner can refund it using `refund_highest_bidder`.

```vyper
@external
def refund_highest_bidder():
    assert msg.sender == self.owner, "unauthorized"
    assert self._epoch_in_progress() == False, "epoch not over"

    refund_amount: uint256 = self.highest_bid
    refund_receiver: address = self.highest_bidder

    self.highest_bid = 0
    self.highest_bidder = empty(address)

    ERC20(WETH).transfer(refund_receiver, refund_amount)
```

But there is no other limit so the owner can refund without deposit using `refund_highest_bidder` when `settle` and deposit to Vault works normally. In this case, the attacker can front-run `refund_highest_bidder` and call `settle` so the owner has no option to refund. 


## Impact
The owner can't refund when deposit to Vault works normally.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L212
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L314-L325

## Tool used
Manual Review

## Recommendation
Make sure when `refund_highest_bidder` is called and restrict `settle` more so it can't be called at the same time.
