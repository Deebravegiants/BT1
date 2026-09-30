# [M] User can unstake anytime instead of getting locked for 1 year

## Summary
Severity: Medium
Contest weight: 0.3635
Dataset id: 5757
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unrestricted early‑withdrawal bug in the staking contract. The unstake function does not enforce the one‑year lock period that the protocol specifications require, so any staker can call unstake at any moment after depositing. The root cause is the absence of a time‑based condition that checks whether the current block timestamp is greater than or equal to the stake start time plus the required lock duration (approximately 366 days). Because this check is missing, the contract’s business logic that is supposed to lock funds for a year is never executed. An attacker or any regular user can simply invoke unstake immediately after staking, receiving their principal and any accrued rewards without waiting. This can be exploited by calling the unstake method directly, bypassing the intended vesting schedule, and may lead to a rapid outflow of capital that undermines the tokenomics, reward distribution, and overall security assumptions of the protocol. The issue manifests whenever a position is created; there is no conditional branch that restricts withdrawal based on elapsed time, so it occurs for every staker regardless of role or amount. It was discovered during a manual audit that compared the contract implementation against the documented requirements, revealing that the time lock logic was never implemented. The problem can be subtle because the contract still functions—users can stake and unstake—but it violates the expected economic model, making it easy to overlook without a specific test for the lock period. To remediate, the contract should include a verification step in the unstake routine that asserts the current timestamp is at least the stake start time plus one year, for example by checking Clock::get()?.unix_timestamp against self.position.start_time plus the lock interval. This change restores the intended lock behavior, aligns the contract with its specifications, and prevents premature fund extraction. The bug belongs to the class of missing‑validation or business‑logic enforcement errors, where a critical condition (time lock) is omitted, leading to unintended state transitions such as immediate fund release, which users may perceive as “my stake disappears instantly” or “I can withdraw my money right away even though it should be locked.”

## Recommendation
Consider implementing a time check in unstake() function that only allows stakers to unstake after 1 year has passed since their initial stake.
```solidity
+ assert!(Clock::get()?.unix_timestamp >= self.position.start_time + (366 * 24 * 60 * 60));
```
