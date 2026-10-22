# [H] H-05 | Decrease Orders Can Output 2 Tokens

## Summary
Severity: High
Contest weight: 0.1611
Dataset id: 21945
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The afterOrderExecution function in the GmxUtils contract assumes that only one output token will
be returned. However, GMX decrease position orders can output two tokens instead of a single token
if the decrease position swap fails.
As a result, this scenario is not properly accounted for in the _handleReturn function, which is
responsible for calculating the user's withdrawal amounts and updating global states. This can
result in users receiving less than they should and can corrupt the accounting.

## Recommendation
Update the afterOrderExecution function in the GmxUtils contract to read and pass down the
secondaryOutputToken and secondaryOutputAmount in the same way as the outputToken and
outputAmount.
Then, modify the _handleReturn function in the PerpetualVault contract to account for both tokens.
