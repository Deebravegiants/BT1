# [M] Malicious Users Can Force An Emergency Settlement On Any Vault

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-notional
Published: 2022-10-13
Source: https://github.com/sherlock-audit/2022-09-notional-judging/issues/103
Type: sherlock-finding

## Details
xiaoming90

high

# Malicious Users Can Force An Emergency Settlement On Any Vault

## Summary

Malicious users can force an emergency settlement on any vault causing a denial of service.

## Vulnerability Detail

The following function shows that an emergency settlement can only be triggered if the total number of BPT held by the vault exceeds the BPT threshold. 

https://github.com/sherlock-audit/2022-09-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/internal/settlement/SettlementUtils.sol#L86

```solidity
File: SettlementUtils.sol
86:     function _getEmergencySettlementParams(
87:         StrategyContext memory strategyContext,
88:         PoolContext memory poolContext,
89:         uint256 maturity,
90:         uint256 totalBPTSupply
91:     )  internal view returns(uint256 bptToSettle) {
92:         StrategyVaultSettings memory settings = strategyContext.vaultSettings;
93:         StrategyVaultState memory state = strategyContext.vaultState;
94: 
95:         // Not in settlement window, check if BPT held is greater than maxBalancerPoolShare * total BPT supply
96:         uint256 emergencyBPTWithdrawThreshold = settings._bptThreshold(totalBPTSupply);
97: 
98:         if (strategyContext.totalBPTHeld <= emergencyBPTWithdrawThreshold)
99:             revert Errors.InvalidEmergencySettlement();
```

Another point to note is that a major side-effect of an emergency settlement is that the vault will be locked up after the emergency settlement. No one is allowed to enter the vault and users are only allowed to exit from the vault by taking their proportional share of cash and strategy tokens. Thus, if anyone can force an emergency settlement on any vault, it would cause a widespread denial of service.

However, it is possible for anyone to force an emergency settlement on any vault.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-notional-judging/issues/103_
