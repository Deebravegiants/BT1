# [H] Lack of frontrunning protection in resolveCondition allows unfair advantage

## Summary
Severity: High
Contest weight: 0.0954
Dataset id: 14910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The EnhancedSportsPrediction::resolveCondition function can be frontrun by malicious users. Since there is no check for endTime, a user can monitor the mempool for a resolveCondition transaction, extract the winningOutcome, and place a large bet on it before the condition is resolved.

## Recommendation
Divide the resolveCondition logic into two separate functions: one to block trading and another to set the winning outcome.
