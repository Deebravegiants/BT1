# [H] H-09 | Migration Inconsistencies

## Summary
Severity: High
Contest weight: 0.2433
Dataset id: 21416
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to documentation there is a time where both old contracts and new contracts are live and used by keepers. This can create massive inconsistency in the system such as: 1. Borrowing fee calculations are different between systems which will lead to both different borrowing fee's for users between systems and also different market token pricing's for the system which can have catastrophic effect. 2. While old system continue to send excess fees to account, new system will send them to receiver. Which can be especially problematic for integrators who changed their system according to new implementation and can't send excess fees to receiver anymore. 3. Take profit and stop-loss orders that are opened with new contracts will be added to autoCancelList but if the position is closed/liquidated with the old keeper, this lost won't be cleared. Which in turn, users can experience unexpected position openings in the future if they continue to use the system.

## Recommendation
Try to not use both contracts at the same time, if they will be used, be sure to not set optimalBorrowingFactor until old system abandoned and also inform users and integrations about inconsistencies that may arise because of this situation.
