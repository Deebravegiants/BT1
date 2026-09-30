# [M] M-25 | Closed Amt Not Seized If Its Value Is < 0

## Summary
Severity: Medium
Contest weight: 0.0958
Dataset id: 162
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _validateClosePositionWithAction function checks if the position is liquidatable and if so seizes its closeBoundedPositionValue and gives it the vault.
This check happens with the neutral price and later on, it calculates the value of the position with the price rounded down by the pyth interval and reduced by the position fee.
Therefore the value of the position could be < 0, and in that case the closeBoundedPositionValue is not seized and nothing happens as the rest of the function is only executed if (data.positionValue > 0). In this case, the closeBoundedPositionValue is stuck in the system.

## Recommendation
Seize the closeBoundedPositionValue if the position value is <= 0.
