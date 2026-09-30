# [M] MeritDutchAuction.sol doesn't have timestamp protection

## Summary
Severity: Medium
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# MeritDutchAuction.sol doesn't have timestamp protection

## Summary
MeritDutchAuction's mint does not have timestamp protection.

## Vulnerability Detail
The MeritDutchAuction calculates the price of minting by using the current block timestamp as `getPriceAt(time)` during and after the auction. But an user might be interested to mint only during a brief time interval or before the auction has ended.

## Impact
The user is unable to control its transaction and it might be interest to mint only in a time interval or before auction ending

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
## Tool used

Manual Review

## Recommendation
Insert timestamp protection
