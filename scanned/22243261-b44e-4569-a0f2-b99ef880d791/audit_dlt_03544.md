# [M] Lack of input validation on onlyOwner critical parameters

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-pooltogether
Published: 2021-06-23
Source: https://github.com/code-423n4/2021-06-pooltogether-findings/issues/55
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The owner (potentially untrustworthy/malicious) of the prize pool is allowed to set a liquidation cap (for guarded launch) and the credit rate and limit parameters which affect the crucial fairness of the pool. However, there is no input validation on these critical parameters which could allow accidental/intentional setting of very low/high values which could affect UX and fairness perception.

Impact: Owner sets these to values considered unsafe or unfair, which impacts the safety and fairness of the pool. Users do not deposit funds or withdraw which affects the pool performance and utility.

## Proof of Concept

Reference: See similar Medium-severity findings 21 in Trail of Bits audit of 0x Protocol: https://github.com/trailofbits/publications/blob/master/reviews/0x-protocol.pdf

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L893-L912

https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L977-L986

## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add threshold/sanity checks on all owner set critical parameters.
