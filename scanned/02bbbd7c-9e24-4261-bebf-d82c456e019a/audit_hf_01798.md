# [M] Owner has the power to zero-out user's daily interest on rewards

## Summary
Severity: Medium
Contest weight: 0.0751
Dataset id: 9929
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setDepositsActive method resets startTimestamp and lastGlobalUpdate. The owner can front-run each claimReward transaction and by resetting the startTimestamp this will result in 0 requiredRebases in calculateShareFromTime, so the user will lose on his daily interest. On the other side, by resetting lastGlobalUpdate this will make updateGlobalShares never do a rebase, which will never inflate the overallShare which also shouldn't be possible.

## Recommendation
Make the setDepositsActive method callable only once after contract deployment.
