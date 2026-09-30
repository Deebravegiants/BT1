# [H] H-04 | Users Forfeit Their esGMX, bnGMX And GMX Rewards When Entering The Vault

## Summary
Severity: High
Contest weight: 0.3832
Dataset id: 2040
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ExitVault contract, users can deposit GMX and GLP tokens to participate in the vesting of esGMX tokens and get a portion of them as rewards. While the vault is active, for at least a year, the esGMX, bnGMX, and additional GMX rewards generated from the staked tokens in the different reward trackers are neither claimed nor distributed to the participating users. Instead, these accumulated rewards are only claimed by the vault owner upon his exit, when the earlyOwnerExit function is executed and followed by accepting the account transfer. This design results in two significant issues: • Firstly, users effectively forfeit access to their esGMX, bnGMX and GMX rewards for at least the duration of the vault's operation, despite their GMX/GLP stakes contributing to the generation of these rewards. They do not receive any of these rewards during the active period of the vault. • Secondly, the accumulated rewards are eventually claimed solely by the vault owner upon exit, rather than being distributed to the users who actually generate them. This creates a scenario where users' contributions lead to benefits that they do not receive, raising concerns about fairness and discouraging users from participating in the vault due to the deprivation of their rewards. Moreover, this issue fundamentally undermines the benefits that the protocol aims to provide to users. The esGMX, bnGMX and GMX rewards that users miss out on during the vault's operation are likely worth more than the portion of incentives they receive from the esGMX vesting process. This means that users may actually be worse off by participating in the vault, as they forfeit substantial rewards over the course of a full year, rewards that would likely exceed the benefits gained from the esGMX vesting. Consequently, the vault's current design may inadvertently disadvantage users instead of providing the intended incentives.

## Recommendation
Update the vault's reward distribution mechanism to ensure that users receive their fair share of GMX rewards during the vault's active period. Implement a system where the vault regularly claims the accumulated rewards and distributes the GMX among the users according to their staking contributions and the predefined donation and protocol fee percentages. On the other hand, make use of the esGMX rewards accrued to increase the maxVestableAmount in the vault.
