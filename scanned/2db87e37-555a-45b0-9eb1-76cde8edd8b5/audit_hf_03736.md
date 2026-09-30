# [M] _validateRange in Config does not check the input value against boundaries

## Summary
Severity: Medium
Contest weight: 0.0528
Dataset id: 19869
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_validateRange in Config does not check the input value as described value is within the allowed range. However in the function itself the value is only used in sending revert message, but not used in any check against a pre-set boundary.
function does not verify the input value is within an expected range

## Recommendation
Retrieve the min/max of a baseKey and does checking.
