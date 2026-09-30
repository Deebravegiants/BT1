# [M] Insufficient input validation

## Summary
Severity: Medium
Contest weight: 0.0848
Dataset id: 8602
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In GNSStakingV6_4_1::createUnlockSchedule we have the UnlockScheduleInput calldata _input parameter, where most of the fields in the struct are properly validated to be in range of valid values. The issue is that the start field of the UnlockScheduleInput is not sufficiently validated, as it can be too further away in the future - for example 50 years in the future, due to a user error when choosing the timestamp. This would result in (almost) permanent lock of the GNS funds sent to the method.

## Recommendation
Add a validation that the start field is not too further away in the future, for example it should be max 1 year in the future.
