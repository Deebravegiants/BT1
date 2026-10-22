# [M] Limiting amount of NFTs that can be minted per address can causing causing monopoly

## Summary
Severity: Medium
Reporter: 0xhuy0512
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L143
Type: audit-issue

## Details
# Limiting amount of NFTs that can be minted per address can causing causing monopoly

## Summary
Limiting amount of NFTs that can be minted per address can causing monopoly
## Vulnerability Detail
The Auction contract limiting the maximum amount of NFTs that can be minted per address that is 4. But the user who want to buy more can just make another wallet to mint. Moreover, they can make a contract that can mint all NFT in one transaction
## Impact
This can make the NFTs got sold out right after passing start time by one user using front running, causing monopoly
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L143
## Tool used

Manual Review

## Recommendation
Make a whitelist of user who can mint
