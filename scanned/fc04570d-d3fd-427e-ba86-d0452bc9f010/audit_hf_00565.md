# [M] M-06 | Protocol Will Be DoS'd When Private Mode True

## Summary
Severity: Medium
Contest weight: 0.0438
Dataset id: 2027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service condition in the GMX reward tracker caused by the boolean flag inPrivateClaimingMode. When this flag is set to true, the contract disables the public claim functionality; any attempt to claim rewards triggers a revert because the claim action is no longer enabled. Moreover, the internal function _updateVester, which is invoked by several other protocol operations, also reverts when the flag is active. The root cause is that the private‑claiming mode is implemented without isolating its effect to only the intended claim path, so other functions that rely on vesting updates inherit the same revert behaviour. An attacker or a privileged account that can toggle the flag can therefore lock the reward‑claiming mechanism and cause any transaction that touches the vesting logic to fail. This can be exploited simply by setting inPrivateClaimingMode to true, after which users who try to claim their accrued rewards receive a transaction failure and see no change in their token balance. The impact is that users are unable to receive expected rewards, balances appear unchanged, and the protocol may be unable to process vesting updates, effectively freezing reward distribution for the duration of the flag being true. The condition occurs whenever the flag is true, regardless of who initiates the claim or vesting update. Affected parties include token holders, reward claimants, and any component of the protocol that depends on vesting state updates. The issue was discovered during a security audit that examined the interaction between the private‑claiming mode and the vesting update logic, noting that the revert path was not guarded. It can be hard to notice because the flag is intended for a legitimate private mode, and the UI may simply hide the claim button without clearly indicating that underlying transactions will revert, leading users to think the contract is malfunctioning. To remediate, the contract should either separate the private‑claiming mode from the vesting update path, add explicit checks before calling _updateVester when the flag is true, or provide an administrative mechanism to disable the flag promptly. At a minimum, the risk of funds being temporarily inaccessible should be documented so that users understand the possibility of a denial‑of‑service scenario.

## Recommendation
Document the risk that funds can be DoS'd for periods of time when this variable is set to true.
