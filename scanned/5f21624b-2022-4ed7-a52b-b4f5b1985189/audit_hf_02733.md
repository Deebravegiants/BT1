# [M] Lack of reimbursement mechanism for incorrect bets leads to fund locking

## Summary
Severity: Medium
Contest weight: 0.0556
Dataset id: 14914
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the EnhancedSportsPrediction::claimPayout function, if all users bet on the wrong outcome, the funds remain locked in the contract due to the line if (outcomePool == 0) revert NoBetsOnOutcome();. Currently there is no mechanism to reimburse users or collect the funds as house fees.

## Recommendation
In such situation, either collect the funds as house fees or implement a mechanism to reimburse users with their bets (possibly minus the house fee).
