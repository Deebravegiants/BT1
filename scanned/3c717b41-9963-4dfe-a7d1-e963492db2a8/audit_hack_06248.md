# [H] Auction can be force started and first token force minted by calling `settle()` before the auction was launched

## Summary
Severity: High
Reporter: ABA
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L174-L213
Type: audit-issue

## Details
# Auction can be force started and first token force minted by calling `settle()` before the auction was launched

## Summary

Auction can be force started and first token force minted by calling `settle()` before the auction was launched

## Vulnerability Detail

The [`settle()` function](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L174-L213) is used to finalize a finished auction (mint the won NFT to the winner) and send the won bid amount to the vault. 

The function itself, _is callable by anybody_, the only restriction it has is that it reverts if an auction epoch is running, by checking `_epoch_in_progress()`
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L185

This check however only verifies that this function is not executed during an auction. There is no check if the auction has actually started, thus all conditions are met.

The logical execution flow is as follows:

- ` assert self._epoch_in_progress() == False, "epoch not over"` passes because it checks for `return block.timestamp >= self.epoch_start and block.timestamp <= self.epoch_end`;  `epoch_start` and `epoch_end` are defaulted as 0, so the functions returns **False**

- `highest_bidder` is defaulted to 0, so winner is initially set to `empty(address)`
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L187

- winner is then set to the `FALLBACK_RECEIVER` because of the previous value of winner being the 0 address
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L191-L192

- this being the first run/execution of `settle()`, the `current_epoch_token_id` and `max_token_id` variables have their initial value. `current_epoch_token_id` will simply be set to the initial default value + 1
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L200-L201

- the NFT is then minted to the `FALLBACK_RECEIVER` address
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208

- because `winning_amount` is also set to 0 as the default, the Vault `register_deposit(...)` is not called. If it would have been called, the transaction would of reverted (vault checks for this)
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L210-L212

Another issue that arrise from the above execution is that the __auction itself is force started__:
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L202-L203

## Impact

- anybody can force start the auction at any time before the `start_auction(...)` function is called by the project owners by simply calling `settle()`. This can lead to operational and project failure (e.g. community was not announced or were expecting a different date)
- the first NFT is minted to the `FALLBACK_RECEIVER`. Although in the possession of the protocol, the core logic of the project (have [16 tokens mintable to users](https://unstoppabledefi.medium.com/fair-funding-campaign-662131dfa3f6)), along with any benefits to users is lost. This effectively would also reduce the total supply available to mint for users by 1.
- a minimum loss of `RESERVE_PRICE` ETH is encored by the protocol (1 ETH as [declared by them](https://unstoppabledefi.medium.com/fair-funding-campaign-662131dfa3f6)). This is because to bid, a minimum value of `RESERVE_PRICE` ETH is required
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L149
One could argue that no loss can theoretically happen if nobody bids at all in the first round. ITW (in the wild) experience has shown us that the initial launch of a project is usually followed by "hype" and would almost certainly result in a bid. This can practically be considered a loss.

## Code Snippet

The following test `test_settle_called_before_start_auction_issue` can be added in `test_AuctionHouse_settle.py` to show that, the code is in fact vulnerable. 
```Python
def test_settle_called_before_start_auction_issue(owner, house, nft):
    # no house start_auction!
    token_id = house.current_epoch_token_id()
    default_epoch_start = house.epoch_start()

    assert default_epoch_start == 0  # this validates that the default epoch start is 0 if auction not started

    with boa.reverts():  # invalid token id, owner == 0x0
        nft.ownerOf(token_id)  # this validates that the token_id does not have an owner as of now

    house.settle()

    assert nft.ownerOf(token_id) == owner # this validates that the NFT was minted to the fallback address

    epoch_start_after_settle = house.epoch_start()

    assert epoch_start_after_settle != pytest.ZERO_ADDRESS # this validates that the auction was also started
```

## Tool used

Manual Review

## Recommendation

Add an `auction_started` flag requirement in `settle()`. This flag would only be set in the `start_auction` function. 
Example implementation:
```Python
diff --git a/fair-funding/contracts/AuctionHouse.vy b/fair-funding/contracts/AuctionHouse.vy
index fe470ee..79b56f4 100644
--- a/fair-funding/contracts/AuctionHouse.vy
+++ b/fair-funding/contracts/AuctionHouse.vy
@@ -56,6 +56,8 @@ max_token_id: public(uint256)
 highest_bid: public(uint256)
 highest_bidder: public(address)
 
+auction_started: public(bool)
+
 epoch_start: public(uint256)
 epoch_end: public(uint256)
 
@@ -183,6 +185,7 @@ def settle():
         Resets everything and starts the next epoch / auction.
     """
     assert self._epoch_in_progress() == False, "epoch not over"
+    assert self.auction_started == True, "auction has not started yet"
 
     winner: address = self.highest_bidder
     token_id: uint256 = self.current_epoch_token_id
@@ -237,6 +240,7 @@ def start_auction(_start_time: uint256):
 
     self.epoch_start = start
     self.epoch_end = self.epoch_start + EPOCH_LENGTH
+    self.auction_started = True
 
     log AuctionStart(self.epoch_start, msg.sender)
     log Bid(0, msg.sender, 123)

```
