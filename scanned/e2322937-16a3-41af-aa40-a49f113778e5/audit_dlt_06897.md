# [M] Private sale spoofing

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-foundation
Published: 2022-03-02
Source: https://github.com/code-423n4/2022-02-foundation-findings/issues/46
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-foundation/blob/4d8c8931baffae31c7506872bf1100e1598f2754/contracts/mixins/NFTMarketPrivateSale.sol#L156


# Vulnerability details

## Impact
Similar to [spoofing in finance](https://en.wikipedia.org/wiki/Spoofing_(finance)), users can create private sales with correct signatures but then frontrun the buy with a transfer to a different wallet they control.

No funds are lost as this the NFT <> FETH exchange is atomic but it can be bad if third parties create a naive off-chain centralized NFT market based on this signature feature.
It's also frustrating for the users if they try to accept the private sale but their transaction fails.

## Recommended Mitigation Steps
This is made possible because private sales do not keep the NFT in escrow.
Consider escrowing the NFT also for private sales.
