# [M] DebtManager.manualAllocation vault.totalIdle can be lower than vault.minimum_total_idle()

## Summary
Severity: Medium
Contest weight: 0.3592
Dataset id: 6135
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the manual allocation routine of the DebtManager contract, where the logic that decides whether to skip a rebalancing step does not correctly guard against a situation in which the vault’s idle liquidity falls below the protocol‑defined safety threshold (minimum_total_idle). The code only skips the allocation when two conditions are simultaneously true: the position’s recorded debt exceeds the strategy’s current debt *and* the vault’s totalIdle is less than or equal to the minimum_total_idle. Consequently, if the vault’s idle balance is already below the minimum but the position’s debt is not greater than the current debt, the guard is bypassed and the contract proceeds to allocate additional debt. This logical oversight allows the system to allocate more funds than are safely available, breaking the accounting invariant that idle funds must never drop below the configured minimum. An attacker or a careless user could trigger the allocation path (for example by submitting a deposit or by calling a function that forces a manual allocation) and cause the vault to over‑commit its liquidity. The immediate impact is that subsequent withdrawal requests may fail or return zero, user balances can appear reduced, and in extreme cases the protocol could become insolvent because the accounting model assumes a buffer that no longer exists. The issue manifests only when the vault is already under‑collateralized and a manual allocation is attempted while the position’s debt does not exceed the strategy’s current debt. It was discovered during a manual audit of the DebtManager’s allocation loop, where the auditor noticed that the condition does not cover the case of low idle liquidity independent of the debt comparison. The bug is subtle because the guard appears to check the safety threshold, yet the conjunction with the debt comparison hides the failure mode, making it easy to miss during testing that focuses on typical debt‑increase scenarios. To remediate the problem, the allocation loop should unconditionally skip any operation that would execute while vault.totalIdle() is below vault.minimum_total_idle(), regardless of the debt relationship. In practice this means adding a separate early‑continue check for totalIdle < minimum_total_idle or restructuring the condition so that the safety threshold is evaluated first. This aligns the implementation with the intended business rule that the vault must retain a minimum idle buffer to guarantee user withdrawals and preserve protocol solvency.

## Recommendation
```solidity
// deposit/increase not possible because minimum total idle reached
if (position.debt > strategyData.current_debt && vault.totalIdle() <= vault.minimum_total_idle()) continue;
```
