# [M] Stale oracle price can be used because the oracle source is lack of price refreshness check.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/47
Type: sherlock-finding

## Details
ctf_sec

medium

# Stale oracle price can be used because the oracle source is lack of price refreshness check.

## Summary

Stale oracle price can be used.

## Vulnerability Detail

The code currently uses Aave's oracle price and Aave use chainlink oracle data.

```solidity
5 results - 2 files

dn-gmx-vaults\contracts\libraries\DnGmxJuniorVaultManager.sol:
  1102          // AAVE oracle
  1103:         uint256 price = state.oracle.getAssetPrice(address(token));
  1104  

  1150          uint256 decimals = token.decimals();
  1151:         uint256 price = state.oracle.getAssetPrice(address(token));
  1152  
  1153          // @dev aave returns from same source as chainlink (which is 8 decimals)
  1154:         uint256 quotePrice = state.oracle.getAssetPrice(address(state.usdc));
  1155  

dn-gmx-vaults\contracts\vaults\DnGmxSeniorVault.sol:
  314      function getPriceX128() public view returns (uint256) {
  315:         uint256 price = oracle.getAssetPrice(address(asset));
  316  

  325          // use aave's oracle to get price of usdc
  326:         uint256 price = oracle.getAssetPrice(address(asset));
  327  
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/47_
