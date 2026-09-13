# [M] Missing threshold check on critical protection mechanism minRentalDayDivisor

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/103
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

Minimum rental duration is acknowledged as one of the two critical protection mechanisms for the market functioning. The setMinRental() is called from the constructor with 24*6 which sets the minimum duration to 10 minutes.

However, a threshold check is missing for minRentalDayDivisor in setMinRental() which can be called by the owner at any time. Without this check, this may be accidentally set to a value too high which makes duration very small. This will break the safety assumption of the markets.

## Proof of Concept

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCTreasury.sol#L113
https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCTreasury.sol#L167-L171


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Enforce a threshold check to make sure this is not set to too high a value which will break safety assumptions of the markets.
