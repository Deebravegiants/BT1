# [M] Admin and treasury change should be confirmed.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-floatcapital
Published: 2021-08-05
Source: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/2
Type: code-finding

## Details
# Handle

tensors


# Vulnerability details

## Impact
Inputting the wrong address here could lock out a lot of the funds and smart contract methods. 

## Proof of Concept
https://github.com/code-423n4/2021-08-floatcapital/blob/bd419abf68e775103df6e40d8f0e8d40156c2f81/contracts/contracts/LongShort.sol#L209

https://github.com/code-423n4/2021-08-floatcapital/blob/bd419abf68e775103df6e40d8f0e8d40156c2f81/contracts/contracts/LongShort.sol#L216

## Recommended Mitigation Steps
Require the changed address to confirm the switch (with a pendingAdmin, pendingTreasury variable.
