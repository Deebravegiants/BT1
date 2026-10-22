# [H] MJR-1 Incorrect events parameter

## Summary
Severity: High
Contest weight: 0.0411
Dataset id: 15787
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the lines below:
LendingPair.sol#L252
LendingPair.sol#L267
LendingPair.sol#L282
LendingPair.sol#L291
LendingPair.sol#L306
LendingPair.sol#L321
there are places where we have events which require an affected user address as a parameter, however in these cases msg.sender is wrongly used as a parameter. These functions accept special user parameter that should be used in events instead of msg.sender. The issue marked as major since it can fatally affect the user's side code that is based on events.

## Recommendation
We suggest replacing msg.sender to user.
