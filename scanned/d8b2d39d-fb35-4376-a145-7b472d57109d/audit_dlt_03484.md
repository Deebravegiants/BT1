# [H] Missing zero-address check for the beneficiary address

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-meebits
Published: 2021-04-30
Source: https://github.com/code-423n4/2021-04-meebits-findings/issues/33
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The beneficiary address specified in constructor receives all the proceeds from NFT sales which could be of significant value. However, there is no zero-address validation of this _beneficiary address parameter during initialization in the constructor. Using a zero address by mistake will require redeployment because there is no functionality to change this address after contract deployment.

Given the selling prices of popular NFTs, it may be disastrous to accidentally burn the sale proceeds of even one NFT. 

This will lead to loss of funds from potential revenue.


## Proof of Concept

https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L212

https://github.com/code-423n4/2021-04-redacted/blob/2ec4ce8e98374be2048126485ad8ddacc2d36d2f/Beebots.sol#L387


## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Add zero-address validation for _beneficiary address parameter in constructor.
