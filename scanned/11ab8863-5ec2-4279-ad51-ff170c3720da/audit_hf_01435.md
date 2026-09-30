# [M] M-2 Missing DIAOracleV2Meta.setThreshold() and

## Summary
Severity: Medium
Contest weight: 0.0969
Dataset id: 7448
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue has been located in the setThreshold and setTimeoutSeconds functions of the DIAOracleV2Meta contract. More speciﬁcally, it was found that the functions don't check for zero values in the newThreshold and newTimeoutSeconds parameters. As a result, if zero is assigned as a value, it causes the getValue function to revert and disrupts normal operation.
There also needs to be an upper bound on newTimeoutSeconds. In case of abnormally large newTimeoutSeconds, (0, 0) can bypass DIAOracleV2Meta.sol#L111-L113 so it would affect the median value.

## Recommendation
We advise implementing a validation check in the setThreshold and setTimeoutSeconds functions to ensure that zero is not accepted as an assigned value and also newTimeoutSeconds is less than some reasonable value.
