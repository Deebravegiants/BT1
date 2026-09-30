# [M] CON-1 | Lack Of Parameter Validation

## Summary
Severity: Medium
Contest weight: 0.0920
Dataset id: 19224
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no validation that the THRESHOLD_FOR_DECREASE_FUNDING is less than THRESHOLD_FOR_STABLE_FUNDING. If the config keeper were to invert the thresholds, the funding factor may be decreasing when it should be stable or increasing when it should be decreasing. Furthermore, there is no validation that the MIN_FUNDING_FACTOR_PER_SECOND is less than the MAX_FUNDING_FACTOR_PER_SECOND. As a result, boundMagnitude will bound the value incorrectly.

## Recommendation
Add validation in the Config to ensure THRESHOLD_FOR_DECREASE_FUNDING is less than THRESHOLD_FOR_STABLE_FUNDING. Add validation in the Config to ensure MIN_FUNDING_FACTOR_PER_SECOND is less than MAX_FUNDING_FACTOR_PER_SECOND. A check for the min and max bounds may be included in boundMagnitude as well or the documentation should mention that the validation is done elsewhere.
