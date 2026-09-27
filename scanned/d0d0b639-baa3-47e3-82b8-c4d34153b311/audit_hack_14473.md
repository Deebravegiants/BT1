# [H] Ability to Mint NFTs After Auction End Time

## Summary
Severity: High
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L139
Type: audit-issue

## Details
# Ability to Mint NFTs After Auction End Time

## Summary
There's a vulnerability in the smart contract that allows NFTs to be minted even after the end of the auction. The endTime is defined as the end of the auction, but there is no validation in the mint function to check whether the current time is after endTime.

## Vulnerability Detail
In the smart contract, the endTime variable is meant to represent the end of the auction period. However, the mint function, which is responsible for creating new NFTs, does not include a check to ensure that the current time is before endTime.

This means that, if there are still quantities remaining, users could continue to mint NFTs even after the auction has officially ended according to the endTime variable.

## Impact
User can mint after endTime

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L139

## Tool used

Manual Review

## Recommendation
To mitigate this issue, a condition should be added in the mint function to check that the current time is before endTime.
