# [M] Missing function setParams in Dao

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2021-07-spartan/blob/main/contracts/synthVault.sol#L81
Type: audit-issue

## Details
# Handle

0xsanson


# Vulnerability details

## Impact
The function setParams() in synthVault is supposed to be called by the Dao, but this contract doesn't have it, causing the impossibility to update the parameters by the protocol.

## Proof of Concept
https://github.com/code-423n4/2021-07-spartan/blob/main/contracts/synthVault.sol#L81

## Tools Used
editor

## Recommended Mitigation Steps
Add the setParams() function to Dao.sol.
