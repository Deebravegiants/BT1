# [M] NFTs can get stuck in contracts that don't support ERC-721

## Summary
Severity: Medium
Reporter: ck
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208
Type: audit-issue

## Details
# NFTs can get stuck in contracts that don't support ERC-721

## Summary

NFTs can get stuck in contracts that don't support ERC-721

## Vulnerability Detail

If the NFT is minted to a contract that doesn't support ERC-721, it will be frozen in the contract.
This is because of the use of `mint` instead of `safemint`

## Impact

Bidders would lose their NFTs

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L208

## Tool used

Manual Review

## Recommendation

Use `safemint` instead of `mint` to check received address support for ERC721 implementation.
