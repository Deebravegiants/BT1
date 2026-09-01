# [H] Vault's `totalStrategyTokenGlobal` will not be in sync

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-notional
Published: 2023-01-13
Source: https://github.com/sherlock-audit/2022-12-notional-judging/issues/15
Type: sherlock-finding

## Details
xiaoming90

high

# Vault's `totalStrategyTokenGlobal` will not be in sync

## Summary

The `strategyContext.vaultState.totalStrategyTokenGlobal` variable that tracks the number of strategy tokens held in the vault will not be in sync and will cause accounting issues within the vault.

## Vulnerability Detail

> This affects both the TwoToken and Boosted3Token vaults

The `StrategyUtils._convertStrategyTokensToBPTClaim` function might return zero if a small number of `strategyTokenAmount` is passed into the function. If `(strategyTokenAmount * context.vaultState.totalBPTHeld)` is smaller than `context.vaultState.totalStrategyTokenGlobal`, the `bptClaim` will be zero.

https://github.com/sherlock-audit/2022-12-notional/blob/main/contracts/vaults/balancer/internal/strategy/StrategyUtils.sol#L18

```solidity
File: StrategyUtils.sol
17:     /// @notice Converts strategy tokens to BPT
18:     function _convertStrategyTokensToBPTClaim(StrategyContext memory context, uint256 strategyTokenAmount)
19:         internal pure returns (uint256 bptClaim) {
20:         require(strategyTokenAmount <= context.vaultState.totalStrategyTokenGlobal);
21:         if (context.vaultState.totalStrategyTokenGlobal > 0) {
22:             bptClaim = (strategyTokenAmount * context.vaultState.totalBPTHeld) / context.vaultState.totalStrategyTokenGlobal;
23:         }
24:     }
```

In Line 441 of the `Boosted3TokenPoolUtils._redeem` function below, if `bptClaim` is zero, it will return zero and exit the function immediately.

If a small number of `strategyTokens` is passed into the `_redeem` function and the `bptClaim` ends up as zero, the caller of the `_redeem` function will assume that all the `strategyTokens` have been redeemed.

https://github.com/sherlock-audit/2022-12-notional/blob/main/contracts/vaults/balancer/internal/pool/Boosted3TokenPoolUtils.sol#L432

```solidity
File: Boosted3TokenPoolUtils.sol
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-12-notional-judging/issues/15_
