# [M] M-30 | User's Lockup Period Should Not Change Midway

## Summary
Severity: Medium
Contest weight: 0.0402
Dataset id: 22201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the contract exposing a mutable global lockupPeriod that can be altered by the owner through a setLockupPeriod function. Because the contract checks the unlock eligibility of a stake against this single variable, any change to lockupPeriod retroactively applies to all existing stakes, regardless of when they were created. An attacker with owner privileges can extend the lockup period after users have already deposited tokens, causing those users to remain locked for a longer time than originally promised. This can be exploited by the owner calling setLockupPeriod to a larger value shortly before a large number of users are expected to unstake, effectively preventing them from withdrawing their funds on schedule. The impact is that users experience delayed access to their staked assets, potentially missing market opportunities or being unable to retrieve funds when needed, which violates the economic assumptions of the staking service. The condition occurs whenever the owner invokes the lockup period update after stakes have been made; it does not require any special user interaction. All participants who have staked tokens are affected, including regular users, liquidity providers, and any downstream contracts that rely on the expected unlock time. The issue was discovered during a manual audit that examined state‑variable usage and identified that the lockupPeriod is not snapshot per stake. It can be hard to notice because the contract may appear to function correctly for new stakes, and the UI may simply show a longer countdown without indicating that the policy changed. The proper mitigation is to capture the current lockupPeriod value at the moment a user stakes and store it in the individual Stake record, then reference this stored value when calculating the unlock timestamp during unstake. This change isolates each stake from future policy adjustments, preserving the original agreement and preventing unfair extension of lockup periods.

## Recommendation
When a user stakes, consider storing the current lockupPeriod value in their own Stake struct. And use that value when checking for unlock time in unstake.
