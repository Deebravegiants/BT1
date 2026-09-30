# [M] M-13 | Recall Can Be Frontrunned

## Summary
Severity: Medium
Contest weight: 0.0959
Dataset id: 21601
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Owner has a right to recall a grant and this function returns unclaimed tokens to the owner from the holder. Returning unclaimed tokens:
1. Creates unfair situations between holders. Let’s assume there are two different holders with exact same cliff and release duration parameters but one of them claimed unlocked part of his vesting and the other didn’t claim anything yet. Recalling from both of these holders results in different user balances.
2. Creates a surface for frontrunning attacks. Users can frontrun the recall and claim their vestings’ claimable portion just before the recall.

## Recommendation
Consider adding a new functionality to recall only the remaining portion of a vest alongside recall.
