# [M] M-4 Incorrect Handling of milestoneUnlockedTotal in

## Summary
Severity: Medium
Contest weight: 0.0842
Dataset id: 10439
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This issue has been identified in the getUnlockedTokenAmount function of all the allocation's contracts.
The current implementation includes milestoneUnlockedTotal in the calculation of unlocked tokens, even when the unlocking process is complete. This can result in an overestimation of the unlocked tokens when all tokens have already been fully unlocked.
The issue is classified as Medium severity because it could lead to inaccurate calculations of unlocked tokens.

## Recommendation
We recommend updating the logic to exclude milestoneUnlockedTotal from the calculation once the unlocking process is finished, ensuring a more accurate representation of the unlocked tokens.
