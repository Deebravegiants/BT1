# [M] M-27 | Liquidatable Positions Can Be Opened

## Summary
Severity: Medium
Contest weight: 0.0943
Dataset id: 164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validate open position flow if the maximum leverage is exceeded with the new startPrice the position and it's tick is recalculated. This new tick could be liquidatable in edge cases if the price between init and validate changed drastically but the position is still created.
The primary instance where this becomes a problem is when the liquidation tick actually increases when modified. In these situations a once healthy position can become liquidateable resulting in prior liquidation safeguards not being triggered and allowing liquidatable positions to be opened.

## Recommendation
After modifying the positions leverage check if the position is liquidatable and if so, liquidate the position.
