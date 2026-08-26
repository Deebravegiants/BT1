# [M] fees calculations are not accurate

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-12-amun
Published: 2021-12-16
Source: https://github.com/code-423n4/2021-12-amun-findings/issues/73
Type: code-finding

## Details
# Handle

certora


# Vulnerability details


after that fee is calculated, it is minted to the feeBeneficiary.
simply minting the exact amount results lower fee than it should be.

## Impact
feeBeneficiary will get less fees than it should.
## Proof of Concept
let's assume that the basket assets are worth 1M dollars, and totalSupply = 1M.
the result of `calcOutStandingAnnualizedFee` is 100,00 so the feeBeneficiary should get 100,00 dollars. 
however, when minting 100,00 the totalSupply will increase to 1,100,000 so they will own 100000/1100000* (1M dollars) = 90909.09 dollars instead of 100k
