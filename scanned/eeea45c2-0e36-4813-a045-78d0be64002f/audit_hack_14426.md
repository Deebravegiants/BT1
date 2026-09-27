# [H] Possible to lost NFT

## Summary
Severity: High
Reporter: glcanvas
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# Possible to lost NFT

## Summary

If auction participant is contract -- it may lost NFT, if it don't implement transfer function.

## Vulnerability Detail

In ERC721 contract new minted token sending to a new owner. 
If owner is EOA account he can easily sell token and get profit.
But if owner is Contract it need to additionally check that this contract can interact with this NFT. If it can't -- then minted token might be stuck forever.

## Impact

Minted NFT might be stuck if contract isn't capable to manage NFT. So user might lost savings.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63

## Tool used

Manual Review

## Recommendation

Use `safeMint` instead of `mint` function.
