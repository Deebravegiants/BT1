# [M] Missing cap on LicenseFee

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L140-141
Type: audit-issue

## Details
# Handle

gzeon


# Vulnerability details

## Impact
There is no cap on `LicenseFee`. While change of `LicenseFee` is under 1 day timelock, introducing a  
`maxLicenseFee` can improve credibility by removing the "rug" vector. There is a `minLicenseFee` in the contracts, while imo make little sense to have `minLicenseFee` but not `maxLicenseFee`.

An incorrectly set `LicenseFee` can potentially lead to over/underflow in 
https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L140-141 which is used in most of the function.

## Proof of Concept
https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L177
https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Factory.sol#L77
https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L49

## Recommended Mitigation Steps
Define a `maxLicenseFee`
