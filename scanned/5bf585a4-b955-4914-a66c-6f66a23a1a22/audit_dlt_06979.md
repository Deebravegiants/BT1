# [M] [PNM-004] Calculation of `_secondaryReserveRatio` can be overflowed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-nibbl
Published: 2022-06-24
Source: https://github.com/code-423n4/2022-06-nibbl-findings/issues/273
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-nibbl/blob/8c3dbd6adf350f35c58b31723d42117765644110/contracts/NibblVault.sol#L183


# Vulnerability details

## Description

`uint32 _secondaryReserveRatio = uint32((msg.value * SCALE * 1e18) / (_initialTokenSupply * _initialTokenPrice));` 

`_secondaryReserveRatio` can be overflowed by setting a relatively small `_initialTokenSupply` and `_initialTokenPrice`. The result will be truncated by `uint32`, causing an overflow.

This overflow can bypass all the checks in function `initialize`. Any following functionality will be impacted since the `_secondaryReserveRatio` is incorrect.

## PoC / Attack Scenario

+ The user provide `_initialTokenSupply` and `_initialTokenPrice`, which meets `SCALE * 1e18 == _initialTokenSupply * _initialTokenPrice`
+ The `msg.value` is set as `2 ** 32 + X`, where `MIN_SECONDARY_RESERVE_RATIO <= X <= primaryReserveRatio`. Note that `msg.value` is in Wei, so the deposited fund is not huge.

## Suggested Fix

Add overflow checks.
