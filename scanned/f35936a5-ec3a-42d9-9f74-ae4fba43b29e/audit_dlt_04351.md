# [M] Possible DoS on contracts due to initialized Controller

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/141
Type: sherlock-finding

## Details
cryptphi

medium

# Possible DoS on contracts due to initialized Controller

## Summary
Contracts making an external call to Controller.__Controller_init() would revert if Controller is already initialized.

## Vulnerability Detail
The following contracts make an external call to Controller.__Controller_init() in their initialization functions;

- AaveV3Adapter
- AssetManager
- PureTokenAdapter
- MarketRegistry
- UToken
- Comptroller
- UserManager

Once Controller is initialized by any contract or a user, every other contract making the external call to Controller.__Controller_init() would revert is Controller has already being initialized.

## Impact
Inability for some contracts to be initialized.

## Code Snippet
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/Controller.sol#L95-L100

The following are locations where the external call to initialize Controller are made.

1. https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/asset/AaveV3Adapter.sol#L72

2. https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/asset/AssetManager.sol#L108

3. https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/asset/PureTokenAdapter.sol#L37
 
4. https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/MarketRegistry.sol#L55
 

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/141_
