# [M] `FALLBACK_RECEIVER` is an important address and should be changeable to prevent possible lose

## Summary
Severity: Medium
Reporter: ABA
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L116
Type: audit-issue

## Details
# `FALLBACK_RECEIVER` is an important address and should be changeable to prevent possible lose

## Summary

`FALLBACK_RECEIVER` is an important address and should be changeable to prevent possible lose

## Vulnerability Detail

In `AuctionHouse.vy` the `FALLBACK_RECEIVER` address is used if there are no bids during an epoch to mint the NFT to it. 

This address is only checked to not be 0 address
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L116

and is declared as immutable `FALLBACK_RECEIVER: public(immutable(address))` meaning that if a wrong address is set here, it cannot be change.

Such an important address needs to be changeable in case of typos/mistakes when first setting it.

## Impact

Because the address is used to send NFTs that are not bided on during the auction, if a wrong address is set, any such NFT will be lost. These NFTs have specific roles in the protocol ecosystem, that benefits user. Even if in the possession of the protocol (if no bidder) they could still be used after by the protocol during other campaigns.

## Code Snippet

Setting the address
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L123

Setting it as winner
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L191-L193

Minting to it
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208

## Tool used

Manual Review

## Recommendation

Make `FALLBACK_RECEIVER` a normal, public, address and create a setter for it, executable only by the owner. Also send an event when the change is executed. Example implementation:

```Python
diff --git a/fair-funding/contracts/AuctionHouse.vy b/fair-funding/contracts/AuctionHouse.vy
index fe470ee..17ab45f 100644
--- a/fair-funding/contracts/AuctionHouse.vy
+++ b/fair-funding/contracts/AuctionHouse.vy
@@ -18,7 +18,7 @@
     A bid close to epoch_end extends the auction by 15min since last bid to 
     prevent sniping.
 
-    If an epoch ends with no bids, the NFT is minted to the FALLBACK_RECEIVER 
+    If an epoch ends with no bids, the NFT is minted to the fallback_receiver 
     address.
 
     The owner can change the max_token_id / max number of NFTs minted.
@@ -42,7 +42,7 @@ WETH: public(immutable(address))
 
 vault: public(address)
 
-FALLBACK_RECEIVER: public(immutable(address))
+fallback_receiver: public(address)
 
 EPOCH_LENGTH: public(constant(uint256)) = 60 * 60 * 24  # 1 day in seconds
 TIME_BUFFER: public(constant(uint256)) = 15 * 60  # 15 min in seconds
@@ -98,6 +98,10 @@ event OwnershipTransferred:
     old_owner: indexed(address)
     new_owner: indexed(address)
 
+event FallbackReceiverAddressChanged:
+    old_fallback_receiver: indexed(address)
+    new_fallback_receiver: indexed(address)
+
 
 @external
 def __init__(
@@ -120,7 +124,7 @@ def __init__(
     NFT = _nft_address
     self.vault = _vault_address
     RESERVE_PRICE = _reserve_price
-    FALLBACK_RECEIVER = _fallback_receiver
+    self.fallback_receiver = _fallback_receiver
 
     self.owner = msg.sender
 
@@ -178,7 +182,7 @@ def settle():
         Settles the latest epoch / auction.
         Reverts if the auction is still running.
         Mints the NFT to the highest bidder. 
-        If there are no bids, mints the NFT to the FALLBACK_RECEIVER
+        If there are no bids, mints the NFT to the fallback_receiver
         address.
         Resets everything and starts the next epoch / auction.
     """
@@ -189,8 +193,8 @@ def settle():
     winning_amount: uint256 = self.highest_bid
 
     if winner == empty(address):
-        winner = FALLBACK_RECEIVER
-        log AuctionSettledWithNoBid(token_id, FALLBACK_RECEIVER)
+        winner = self.fallback_receiver
+        log AuctionSettledWithNoBid(token_id, self.fallback_receiver)
 
     # reset for next round
     self.highest_bid = 0
@@ -296,6 +300,23 @@ def set_max_token_id(_new_max_token_id: uint256):
     self.max_token_id = _new_max_token_id
 
 
+@external
+def set_fallback_receiver(_new_fallback_address: address):
+    """
+    @notice
+        Changes the fallback receiver address.
+        Can only be called by owner.
+    @param _new_fallback_address
+        The new address to be used as fallback
+    """
+    assert msg.sender == self.owner, "unauthorized"
+    assert _new_fallback_address != empty(address), "fallback cannot be zero address"
+
+    prev_fallback_receiver: address = self.fallback_receiver
+    self.fallback_receiver = _new_fallback_address
+    log FallbackReceiverAddressChanged(prev_fallback_receiver, self.fallback_receiver)
+
+
 @external
 def set_vault(_new_vault_address: address):
     """
```
