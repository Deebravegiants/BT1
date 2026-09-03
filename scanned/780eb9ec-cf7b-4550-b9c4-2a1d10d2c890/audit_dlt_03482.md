# [H] Missing zero/threshold check for NFT sale duration

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-meebits
Published: 2021-04-30
Source: https://github.com/code-423n4/2021-04-meebits-findings/issues/35
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

A zero or some minimum threshold check is missing for _saleDuration parameter of startSale() function which sets the duration of the public sale of NFTs. If accidentally set to 0 then sales happen at zero price according to the logic in getPrice() leading to missed revenue opportunity. This cannot be corrected even by deployer because of the publicSale boolean check which allows startSale() to be called only once and so fixing an incorrectly set sale duration will require contract redeployment.

Given the selling prices of popular NFTs, it may be disastrous to accidentally set a zero or lower than intended public sale duration for NFTs. 

This will lead to loss of funds from potential revenue.

## Proof of Concept

https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L215-L222

https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L334-L335

## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add zero/threshold check for _saleDuration parameter in startSale().
