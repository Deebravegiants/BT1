# [H] The return value of `transferFrom` on new bidder is not checked and may result in no funds transferred

## Summary
Severity: High
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L170-L171
Type: audit-issue

## Details
# The return value of `transferFrom` on new bidder is not checked and may result in no funds transferred

## Summary
The contract can be manipulated by accepting bid request without checking if the bidder does have the amount of WETH which he is proposing.

## Vulnerability Detail
If a malicious bidder does provide for example `2**256 - 1` as the amount, then the contract will think he beat the last bidder without checking the return value of `transferFrom` causing the contract to run out of WETH, and also denying legitimate users from doing bid.

## Impact
A malicious bidder The contract will have no funds  

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L170-L171

## Tool used
vim
Manual Review

## Recommendation
The return value of `transferFrom` on new bidder should be checked to avoid no funds transferred to the contract
