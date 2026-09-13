# [M] If an AuctionHouse gets stuck, cannot start a new AuctionHouse with same vault

## Summary
Severity: Medium
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L268
Type: audit-issue

## Details
# If an AuctionHouse gets stuck, cannot start a new AuctionHouse with same vault

## Summary

Another issue can result in a state where an AuctionHouse cannot perform any more auctions. In this case, it would be desirable to begin minting the NFTs from another AuctionHouse. However, this is not possible because ownership of the NFT cannot be transferred.

## Vulnerability Detail

Another issue means that, if the max_token gets set too low initially, it cannot be raised: https://github.com/sherlock-audit/2023-02-fair-funding-jkoppel/issues/1

This problem combines with that to mean the auctions will be permanently stuck. Instead, a new vault must be created

## Impact

If the max_token gets set too low initially, it cannot be raised, and a new AuctionHouse for the same vault cannot be created

## Code Snippet

Scroll through the admin functions beginning at https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L268 and notice the lack of a function to change the NFT ownership. 

## Tool used

Manual Review

## Recommendation

Make it possible for owner of an AuctionHouse to transfer ownership of the NFT
