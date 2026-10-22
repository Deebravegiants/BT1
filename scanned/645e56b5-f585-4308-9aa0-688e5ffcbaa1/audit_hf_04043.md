# [M] RFPSimpleStrategy milestones can be set mul-

## Summary
Severity: Medium
Contest weight: 0.5491
Dataset id: 20480
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setMilestones function in RFPSimpleStrategy contract checks if MILESTONES_ALREADY_SET or not by upcomingMilestone index. if (upcomingMilestone != 0) revert MILESTONES_ALREADY_SET(); But upcomingMilestone increases only after distribution, and until this time will always be equal to 0. It can accidentally break the pool state or be used with malicious intentions.
1. Two managers accidentally set the same milestones. Milestones are duplicated and can't be reset, the pool needs to be recreated.
2. The manager, in cahoots with the recipient, sets milestones one by one, thereby bypassing totalAmountPercentage check and increasing the payout amount.

## Recommendation
Fix condition if milestones should only be set once.
```solidity
if (milestones.length > 0) revert MILESTONES_ALREADY_SET();
```
Or allow milestones to be reset while they are not in use.
```solidity
if (milestones.length > 0) {
    if (milestones[0].milestoneStatus != Status.None) revert MILESTONES_ALREADY_IN_USE();
    delete milestones;
}
```
