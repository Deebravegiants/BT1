# [H] startTime_ can be set equal to the endTime_ in the constructor

## Summary
Severity: High
Reporter: 0xeix
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78
Type: audit-issue

## Details
# startTime_ can be set equal to the endTime_ in the constructor

## Summary

In MeritDutchAuction, endTime can be set the same as startTime in the constructor making Dutch auction impossible

## Vulnerability Detail

In the constructor of MeritDutchAuction.sol, different parameters can be set such as startTime_, endTime_ but the only check for the startTime and endTime is this:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78

It checks on whether the remainder after the division by stepSize_ is equal to 0 but it can't reveal if startTime_ == endTime_.

## Impact

High as the crucial feature of the contract can be bypassed making Dutch action not able to work as it should work and also getPriceAt() will always revert due to division by 0. startTime_ and endTime_ parameters are used when calculating totalSteps in getPriceAt() function (substraction) and after that when calculating the price we divide by totalSteps.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-87

## Tool used

Manual Review

## Recommendation

Add check so that startTime != endTime
