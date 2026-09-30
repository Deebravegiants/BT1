# [M] Prediction question string is not emitted in any event

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/84
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The entire prediction market is premised around the question posted to the oracle but this question string is never emitted as an event parameter for off-chain observation. This is critical for transparency and should be included in the event emitted here along with the question ID.

## Proof of Concept

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCMarket.sol#L406

## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add question string to event.
