# [M] MarketCore#_mint should check if the market is not deprecated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-float-capital
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/5
Type: sherlock-finding

## Details
ctf_sec

medium

# MarketCore#_mint should check if the market is not deprecated

## Summary

MarketCore#_mint should check if the market is not deprecated

## Vulnerability Detail

https://github.com/sherlock-audit/2022-11-float-capital/blob/main/contracts/market/template/MarketCore.sol#L246-L257

MarketCore#_mint should check if the market is not deprecated before the minting, as the comment suggested.

```solidity
  /// @dev We have to check market not deprecated after system state update because that is the function that determines whether the market should be deprecated.
```

note the function redeem made the check using checkMarketNotDeprecated modifier

```solidity
  function _redeem(
    uint112 amount,
    address user,
    PoolType poolType,
    uint256 poolTier
  ) internal checkMarketNotDeprecated {
```

## Impact

User's may mint position even after the market is deprecated.

## Code Snippet

https://github.com/sherlock-audit/2022-11-float-capital/blob/main/contracts/market/template/MarketCore.sol#L246-L257

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-float-capital-judging/issues/5_
