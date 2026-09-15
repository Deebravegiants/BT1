# [M] Variable would be underflowed causing further problems

## Summary
Severity: Medium
Reporter: smbv-1919
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L117
Type: audit-issue

## Details
# Variable would be underflowed causing further problems

medium
## Summary
Variable would be underflowed causing further problems

## Vulnerability Detail
During deployment if endTime is set smaller than startTime then when getPriceAt() function is called at that time totalSteps variable will underflow as startTime has value greater than endTime

## Impact
the totalsteps variable will underflow and would further create problem for calculating price of NFT.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L117


## Tool used

Manual Review

## Recommendation
Add  require condition in constructor that the value entered for endTime is greater than startTime so it would solve the problem.
