# [M] M-32 | Neutral Price Used In Init Functions

## Summary
Severity: Medium
Contest weight: 0.1201
Dataset id: 198
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All init functions use the lastPrice (the latest neutral price) for calculations, while the validation functions use prices that were adjusted by the pyth interval up or down to round against the user.
Therefore all the checks and temporary state updates at init are most likely wrong at validation time.
Here are a few examples:
• Slippage checks
• Imbalance checks
• The temporary position between init and validate open position
• SDEX calculations
• When a stuck open position action is removed by the admin the user receives the position value based on a unadjusted start price
These examples will lead to users entering a position at a price they explicitly did not agree too, Protocol reaching an imbalanced state and Incorrect amount of SDEX being burned.

## Recommendation
Use the adjusted price in the init functions instead of the neutral price if the calculation uses the adjusted price in the validation function.
