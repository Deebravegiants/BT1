# [M] startPrice should be lower than endPrice

## Summary
Severity: Medium
Reporter: grearlake
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L80
Type: audit-issue

## Details
# startPrice should be lower than endPrice

## Summary
startPrice should be lower than endPrice

## Vulnerability Detail
With logic of the contract, when the time pass, the price become lower, which is disadvantage for user who buy earlier. So that, all user who intended to buy will buy at the last period for cheapest price

## Impact
reputation loss, since user will buy at lass period

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L80

## Tool used
Manual Review

## Recommendation
set startPrice lower than endPrice, and modify all function related to
