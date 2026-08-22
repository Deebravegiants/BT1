# [M] Inconsistency Of Minimum And Maximum Terms Allowed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bond
Published: 2022-11-17
Source: https://github.com/sherlock-audit/2022-11-bond-judging/issues/19
Type: sherlock-finding

## Details
xiaoming90

medium

# Inconsistency Of Minimum And Maximum Terms Allowed

## Summary

Inconsistency of the minimum and maximum terms allowed for a bond token deployed through Bond Protocol might cause issues and be error-prone.

## Vulnerability Detail

A 'vesting' param longer than 50 years is considered a timestamp for fixed expiry based on the following comment within the codebase.

https://github.com/sherlock-audit/2022-11-bond/blob/main/src/bases/BondBaseSDA.sol#L98

```solidity
File: BondBaseSDA.sol
97:     // A 'vesting' param longer than 50 years is considered a timestamp for fixed expiry.
98:     uint48 internal constant MAX_FIXED_TERM = 52 weeks * 50;
```

Within the `BondFixedTermSDA.createMarket` function, validation is in place at Line 38 to prevent users from creating a market that issues fixed-term bonds that vest less than 1 day or more than `MAX_FIXED_TERM` (50 years).

This shows that the protocol does not intend to support fixed-term bonds that vest less than 1 day or more than `MAX_FIXED_TERM` (50 years).

https://github.com/sherlock-audit/2022-11-bond/blob/main/src/BondFixedTermSDA.sol#L33

```solidity
File: BondFixedTermSDA.sol
33:     function createMarket(bytes calldata params_) external override returns (uint256) {
34:         // Decode params into the struct type expected by this auctioneer
35:         MarketParams memory params = abi.decode(params_, (MarketParams));
36: 
37:         // Check that the vesting parameter is valid for a fixed-term market
38:         if (params.vesting != 0 && (params.vesting < 1 days || params.vesting > MAX_FIXED_TERM))
39:             revert Auctioneer_InvalidParams();
40: 
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bond-judging/issues/19_
