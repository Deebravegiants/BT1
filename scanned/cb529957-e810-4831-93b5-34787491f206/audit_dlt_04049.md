# [M] Malicious Users Can Settle More BPT Than Needed During Emergency Settlement

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/102
Type: sherlock-finding

## Details
xiaoming90

high

# Malicious Users Can Settle More BPT Than Needed During Emergency Settlement

## Summary

Malicious users can settle more BPT than needed during emergency settlement leaving no or little BPT behind to accrue the rewards for the vault shareholders.

## Vulnerability Detail

The current BPT threshold is set to 20% of the total BTP supply based on the environment file provided during the audit.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/scripts/BalancerEnvironment.py#L41

```solidity
File: BalancerEnvironment.py
40:             "oracleWindowInSeconds": 3600,
41:             "maxBalancerPoolShare": 2e3, # 20%
42:             "settlementSlippageLimitPercent": 5e6, # 5%
```

The `maxBalancerPoolShare` will be used to compute the BPT threshold of a vault.

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/internal/BalancerVaultStorage.sol#L60

```solidity
File: BalancerVaultStorage.sol
60:     function _bptThreshold(StrategyVaultSettings memory strategyVaultSettings, uint256 totalBPTSupply) 
61:         internal pure returns (uint256) {
62:         return (totalBPTSupply * strategyVaultSettings.maxBalancerPoolShare) / BalancerConstants.VAULT_PERCENT_BASIS;
63:     }
```

When the total number of BPT held by the vault exceeds the BPT threshold, the emergency settlement will be triggered to settle excess BPT to bring the ratio back to a healthy level.

Assume the following:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/102_
