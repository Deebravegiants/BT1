# [M] Fee Distribution Re-Entrancy

## Summary
Severity: Medium
Contest weight: 0.1251
Dataset id: 390
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `distribute` function of `NFTXFeeDistributor` has no access control and will invoke a fallback on the fee receivers, meaning that a fee receiver can re-enter via this function to acquire their allocation repeatedly potentially draining the full balance and sending zero amounts to the rest of the recipients.

A smart contract with a malicious `receiveRewards` function can re-enter the `distribute` function with the same vault ID, thereby causing the exploit.

Recommend that re-entrancy protection should be incorporated into the `distribute` function. I should note that a seemingly innocuous contract can cause this re-entrancy by simply asking the owners of the project to include an upgrade-able contract that is then replaced for a malicious implementation.

**-[0xKiwi (NFTX) confirmed](https://github.com/code-423n4/2021-05-nftx-findings/issues/11)**

## Recommendation
No recommendation
