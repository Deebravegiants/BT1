# [M] FairFundingToken.mint doesn't check if receiver supports erc721

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208
Type: audit-issue

## Details
# FairFundingToken.mint doesn't check if receiver supports erc721

## Summary
FairFundingToken.mint doesn't check if receiver supports erc721
## Vulnerability Detail
When user settles auction, then FairFundingToken [is minted to him](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208).

Pls, note that this function use [`_mint` function](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L17). It doesn't check that receiver supports erc721. As result token can be minted to the contract that doesn't support it. 

Also in the comments, protocol devs mentioned that they didn't use safe mint in order `to avoid potential DoS issue when settling an auction`. But still i guess that check should be added.
## Impact
Token can be minted to the contract that doesn't support it.
## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
Check that if receiver is contract, it supports erc721.
