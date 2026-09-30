# [?] Use the withdraw pattern to avoid the 'King of the Ether' security vulnerability

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2018-12-18
Source: https://github.com/vyperlang/vyper/commit/0c1933dc8ab9b32fc3af63ff6266aec0b377a5ac
Type: security-commit

## Details
Use the withdraw pattern to avoid the 'King of the Ether' security vulnerability

## Patch
### examples/auctions/simple_open_auction.vy
```diff
@@ -13,6 +13,9 @@ highestBid: public(wei_value)
 # Set to true at the end, disallows any change
 ended: public(bool)
 
+# Keep track of refunded bids so we can follow the withdraw pattern
+pendingReturns: public(map(address, wei_value))
+
 # Create a simple auction with `_bidding_time`
 # seconds bidding time on behalf of the
 # beneficiary address `_beneficiary`.
@@ -33,12 +36,21 @@ def bid():
     assert block.timestamp < self.auctionEnd
     # Check if bid is high enough
     assert msg.value > self.highestBid
-    if not self.highestBid == 0:
-        # Sends money back to the previous highest bidder
-        send(self.highestBidder, self.highestBid)
+    # Track the refund for the previous high bidder
+    self.pendingReturns[self.highestBidder] += self.highestBid
+    # Track new high bid
     self.highestBidder = msg.sender
     self.highestBid = msg.value
 
+# Withdraw a previously refunded bid. The withdraw pattern is
+# used here to avoid a security issue. If refunds were directly
+# sent as part of bid(), a malicious bidding contract could block
+# those refunds and thus block new higher bids from coming in.
+@public
+def withdraw():
+    pending_amount: wei_value = self.pendingReturns[msg.sender]
+    self.pendingReturns[msg.sender] = 0
+    send(msg.sender, pending_amount)
 
 # End the auction and send the highest bid
 # to the beneficiary.
```
