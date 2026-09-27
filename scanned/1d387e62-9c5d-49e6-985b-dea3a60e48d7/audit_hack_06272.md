# [H] Hightest_bidder can loss funds due to lack of check

## Summary
Severity: High
Reporter: MyFDsYours
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L314-L325
Type: audit-issue

## Details
# Hightest_bidder can loss funds due to lack of check

## Summary
Hightest_bidder can loss funds due to lack of check

## Vulnerability Detail

In AuctionHouse.vy contract in the refund_highest_bidder function the owner can decide to refund the highest_bidder. But in the transfer function the check of the returned value is not done assuming this one will always return true (never failed) 

## Impact
Hightest_bidder will loss his deposit bid, because (highest_bid is set to 0 and highest_bidder is set to empty address)   highest_bidder will not be able to call any function to get refunded.

## Code Snippet
[AuctionHouse.vy#L314-L325](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L314-L325)
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

## Tool used

Manual Review

## Recommendation

Assert that the transfer call has worked proprely

```diff
@@ -322,4 +322,5 @@ def refund_highest_bidder():
     self.highest_bid = 0
     self.highest_bidder = empty(address)
 
-    ERC20(WETH).transfer(refund_receiver, refund_amount)
+    assert ERC20(WETH).transfer(refund_receiver, refund_amount), "transfer to highest_bidder failed"
```
