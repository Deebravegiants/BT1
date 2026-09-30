# [M] Smart users can wait for near the end of an auction to Front run the last user and mint on the cheapest price and deny him the NTFs

## Summary
Severity: Medium
Reporter: Musaka
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53-L54
Type: audit-issue

## Details
# Smart users can wait for near the end of an auction to Front run the last user and mint on the cheapest price and deny him the NTFs

## Summary
Smart users can wait for near the end of an auction to Front run the last user and mint on the cheapest price and deny him the NTFs
## Vulnerability Detail
The lack of checks and the opportunity of NTFs at a cheaper price attracts bots and MEVs who exploit the protocol for an easy profit. Common scenario for these dutch auctions is for an MEV to wait until the last NTFs remain and front-run the last buyer, getting the NTFs at the cheapest possible price and denying him the opportunity to buy them. After that bot makers usually sell them at second markets for easy profits.
## Impact
User experience worsens, MEVs get the NTFs at a lower price and dump them on secondary markets.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53-L54
## Tool used

Manual Review

## Recommendation
It is recommended to use white lists for the [mint](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L53-L54) function.
