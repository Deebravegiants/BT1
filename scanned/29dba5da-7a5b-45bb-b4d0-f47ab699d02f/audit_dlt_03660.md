# [M] Admin Can Broke All Functionality Through Weth Address

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-canto-v2
Published: 2022-07-02
Source: https://github.com/code-423n4/2022-06-canto-v2-findings/issues/173
Type: code-finding

## Details
# Lines of code

https://github.com/Plex-Engineer/lending-market-v2/blob/main/contracts/Comptroller.sol#L1479


# Vulnerability details

## Impact

On the protocol, almost all functionality is constructed through WETH address. however, If the admin is set to WETH address mistakenly, user could not claim through (https://github.com/Plex-Engineer/lending-market-v2/blob/main/contracts/Comptroller.sol#L1381). Admin can break the protocol.

## Proof of Concept

https://github.com/Plex-Engineer/lending-market-v2/blob/main/contracts/Comptroller.sol#L1479

## Tools Used

Code Review

## Recommended Mitigation Steps

Set WETH address through initializer or change it through governance.
