# [M] Fee on transfer tokens do not work within the protocol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-10-defiprotocol
Published: 2021-10-10
Source: https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/78
Type: code-finding

## Details
# Handle

tensors


# Vulnerability details

Fee on transfer tokens transfer less tokens in than what would be expect.
This means that the protocol request incorrect amounts when dealing with these tokens.

https://github.com/code-423n4/2021-10-defiprotocol/blob/7ca848f2779e2e64ed0b4756c02f0137ecd73e50/contracts/contracts/Basket.sol#L256

The protocol should use stored token balances instead of transfer for calculating amounts.
