# [M] M-01 Feed latest answer not validated (may be old, may be down)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/127
Type: sherlock-finding

## Details
GalloDaSballo

medium

# M-01 Feed latest answer not validated (may be old, may be down)

## Summary

PricerInternal is not checking for feed answer stalenss.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L52

`updatedAt` field from oracle is not checked.

## Vulnerability Detail

## Impact

Oracle may be down, not updated due to network congestion or network attack, and without the extra check the system will accept a stale / old price at face value.

## Code Snippet

## Tool used

Manual Review

## Recommendation

Add a check for staleness like the following:

https://github.com/GalloDaSballo/Super-Simple-Options/blob/7b817bb62be089116ff45502c370d2018d6cf62e/contracts/SuperSimpleCoveredCall.sol#L90



Duplicate of #137
