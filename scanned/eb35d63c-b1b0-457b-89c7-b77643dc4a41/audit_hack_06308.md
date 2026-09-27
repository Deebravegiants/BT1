# [M] [M-02] Incorrect Access Control

## Summary
Severity: Medium
Reporter: DevABDee
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175
Type: audit-issue

## Details
# [M-02] Incorrect Access Control

## Summary
`AuctionHouse.settle()` should be an `onlyOwner` function 

## Vulnerability Detail
The `AuctionHouse.settle()` is used to settle the auction and mint the MintableNFT to the winner's address.
The `MintableERC721.mint()` is `onlyOwner` function. That means only the owner can mint NFTs to the winner's address. 
So `msg.sender == owner` should be checked in the `AuctionHouse.settle()` as well and in the first place.

## Impact
- Incorrect Access Control
- Unexpected behavior might happen 

## Code Snippet
- [AuctionHouse.settle():#L175](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L175)
- [MintableERC721.mint:#L16](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L16)

## Tool used

Manual Review

## Recommendation
Make sure that `AuctionHouse.settle()` is only owner callable:
```vyper
assert msg.sender == self.owner, "unauthorized"
```
