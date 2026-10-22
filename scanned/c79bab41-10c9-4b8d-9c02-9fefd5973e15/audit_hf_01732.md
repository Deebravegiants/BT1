# [H] MJR-1 Changing the shared variable can affect previous votes

## Summary
Severity: High
Contest weight: 0.0389
Dataset id: 9448
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the lines Voting.sol#L126-L133 in the unsafelyChangeVoteTime() method is a change in the common for all voting variable voteTime.
Changing this variable will extend or shorten the voting time on existing voting.
This will affect the voting results, because the process will not go as planned when creating a vote.
So this action is potentially dangerous and may bring the unexpected side effects.

## Recommendation
It is recommended to save the value of the variable voteTime in the structure Vote.
This will be done in the same way as for the supportRequiredPct and minAcceptQuorumPct variables.
