# [M] Iterating over unbounded array can run out of gas

## Summary
Severity: Medium
Contest weight: 0.0993
Dataset id: 6487
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an user wants to unstake from the StakingPool, a for-loop will iterate over all of his stake positions to unstake the relevant indexes. However, this loop will go over all of the past position as well, and in long period of time, if the user interacts with the protocol many times, this array can grow too big and the call can exceed the block gas limit which will DoS the StakingPool.
for (uint i; i < userIssueIndexs.length; i++) {
uint index = userIssueIndexs[i];
if (index >= indexStart) {
Issue storage issueInfo = issues[index];
if (issueInfo.isStaking) {
unstakeAmount += issueInfo.issueAmount;
issueInfo.isStaking = false;

## Recommendation
Consider popping the unstaked positions from the userIssueIndex[].
