# [M] Missing cap on `LicenseFee`

## Summary
Severity: Medium
Contest weight: 0.1951
Dataset id: 1269
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no cap on `LicenseFee`. While change of `LicenseFee` is under 1 day timelock, introducing a  
`maxLicenseFee` can improve credibility by removing the “rug” vector. There is a `minLicenseFee` in the contracts, while imo make little sense to have `minLicenseFee` but not `maxLicenseFee`.

An incorrectly set `LicenseFee` can potentially lead to over/underflow in [Basket.sol#L140-141](https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L140-141) which is used in most of the function.

## Proof of Concept
[Basket.sol#L177](https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L177)  
[Factory.sol#L77](https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Factory.sol#L77)  
[Basket.sol#L49](https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L49)

## Recommendation
Define a `maxLicenseFee`

Generally it is intended for the publishers to act correctly and the timelock is intended to prevent incorrect values from making it all the way through, however there is validity in reducing how the fee can be modified, such as reducing how much any one fee change can change the fee. I would consider this a low risk issue.

It seems like changes to `licenseFee` could potentially brick the contract as `handleFees()` underflows, preventing users from minting/burning tokens. I’d deem this as `medium` severity due to compromised protocol availability.
