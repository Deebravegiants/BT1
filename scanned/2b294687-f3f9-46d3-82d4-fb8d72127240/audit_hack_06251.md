# [M] Attacker calls `settle` before `start_auction` to consume the first NFT and start auction without owner role

## Summary
Severity: Medium
Reporter: XKET
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L185
Type: audit-issue

## Details
# Attacker calls `settle` before `start_auction` to consume the first NFT and start auction without owner role



## Summary
An attacker can call `AuctionHouse.settle` before `start_auction` and the first NFT can't be sold during auction and auction starts without owner's permission.

## Vulnerability Detail

`AuctionHouse.settle` only checks if an epoch is in progress.

```vyper
175     def settle():
            ...
185         assert self._epoch_in_progress() == False, "epoch not over"
```
So an attacker can call this function when the auction is not actually started. In fact, `AuctionHouse.settle` requires owner role of AuctionHouse so only the owner can start auction.

```vyper
217     def settle():
            ...
227         assert msg.sender == self.owner, "unauthorized"
```
But an attacker can bypass this limit using settle and the admin can't control when to start the auction. And there is another exploit in this case. When settle runs before `start_auction`, `_start_token_id` is minted to `FALLBACK_RECEIVER`, and the auction house can't proceed the auction for the first id.
```vyper
191     if winner == empty(address):
192         winner = FALLBACK_RECEIVER
193         log AuctionSettledWithNoBid(token_id, FALLBACK_RECEIVER)
        ...
208     MintableNFT(NFT).mint(winner, token_id)
```

## Impact

An attacker can start auction without owner role and the owner can't decide when to start the auction. And the first NFT of the auction house will be minted to `FALLBACK_RECEIVER` and it can't be sold during the auction.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175-L185
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L217-L227
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L187-L208


## Tool used
Manual Review

## Recommendation
Check if the auction is started in `settle` function
