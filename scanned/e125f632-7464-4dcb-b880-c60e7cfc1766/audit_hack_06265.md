# [M] Duplicate tokens sold when calling set_max_token_id after end of auctions

## Summary
Severity: Medium
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L201
Type: audit-issue

## Details
# Duplicate tokens sold when calling set_max_token_id after end of auctions

## Summary

If the auction runner increases the number of tokens being auctioned after the previous max token ID was sold, then the next auction will be for the same NFT. The auction will proceed as normal, but then fail on settlement when trying to mint a duplicate NFT.

## Vulnerability Detail

1. Create an auction with start token 1, max token 1
2. Run the auction to completion
3. Settle the auction. NFT is minted with ID 1. current_epoch_token_id will remain 1
4. Call set_max_token_id to increase max_token_id to 2
5. Call start_auction
6. Auction will run for another NFT, also of ID 1
7. Finish auction
8. In settle(), the call to MintableNFT(NFT).mint will revert

## Impact

Cannot usefully extend the auctions after they finish

## Code Snippet

self.current_epoch_token_id is incremented for the next auction 

See https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L201

After calling set_max_token_id and then start_auction, a new auction will be started for a duplicate NFT. See https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L217

## Tool used

Manual Review

## Recommendation

Increment current_epoch_token_id in `settle` even if max_token_id is reached
