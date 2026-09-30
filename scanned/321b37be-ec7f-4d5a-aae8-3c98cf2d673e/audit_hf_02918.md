# [M] SQDF-2 | Arbitrary Voting Results

## Summary
Severity: Medium
Contest weight: 0.0515
Dataset id: 16242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the resultVote function, the if statements that determines which finalVoteDecision to return are placed inside of the for loop that counts the votes. Therefore the finalVoteDecision will be arbitrarily based on whichever votes happen to be first in the votes list.

## Recommendation
Move the if statements determining finalVoteDecision after the for loop, or preferably refactor the voting entirely per SQDF-3.
