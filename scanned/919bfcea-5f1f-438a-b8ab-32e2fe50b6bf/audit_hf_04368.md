# [M] M-02 | Missing Validations For Grants

## Summary
Severity: Medium
Contest weight: 0.0979
Dataset id: 21574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
grant only validates if the array params match in length, but there are some crucial validations that should be enforced to correctly grant tokens to a holder:
- Validate that the start and cliff times are in the future.
- Ensure that the cliff time is not before the start time.
- Ensure that the amounts being granted are greater than zero.
- duration > 0
- cliffTime < startTime + duration
Additionally, when the owner creates a regrant, it will add the new amount to the exiting grant, but it will overwrite the timestamps and durations. Setting a shorter duration can allow the user to claim all tokens immediately.

## Recommendation
Consider adding the validations above to correctly create a token grant.
