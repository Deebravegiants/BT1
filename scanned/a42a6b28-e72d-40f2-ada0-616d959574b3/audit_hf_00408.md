# [M] Hardcoded gas for bridge trans-

## Summary
Severity: Medium
Contest weight: 0.4216
Dataset id: 1810
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Code sets static hardcoded gas for all the bridge messages but the issue is that commands GET_INCENTIVES and GET_FEES consumes dynamic amount of gas based on unclaimed epochs and total epochs so leading to stuck messages, i.e. needing manual intervention to deliver the message.
Commands GET_INCENTIVES and GET_FEES are used to collect fee and incentives from IncentiveVotingReward and FeesVotingReward in the leaf chains for users. The amount of gas required for those transactions in the leaf chains depends on the unclaimed epochs of the user and total snapshot counts as code loops through all the unclaimed epochs and also perform a binary search inside all the snapshots. Also user can specify multiple tokens (up to 5) in those commands so the gas consumption may be differ based on number of tokens user specifies. In the current configurations, code uses 440K and 220K gas for those commands:
```solidity
if (_command == Commands.GET_INCENTIVES) return 440_000;
if (_command == Commands.GET_FEES) return 220_000;
```
These hardcoded gas amounts won't be enough to perform transactions on the leaf chain if users didn't claimed their rewards for some times.
Users need to pay for additional gas in a separate transaction in order to deliver their message to the destination chain.

## Recommendation
Allow the user to pay for additional gas.
