# [M] M-28 | Validate Deposit Ignores Funding

## Summary
Severity: Medium
Contest weight: 0.0758
Dataset id: 172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _validateDepositWithAction function uses either the available vault balance at init for the share price calculation or applies the PnL of the current price on it, whichever is bigger, but does not take funding into account.
Therefore, if the longs paid funding fees to the vault between initiation and validation of a deposit the user receives more assets than the user should and the other way around.

## Recommendation
Consider incorporating the latest vault funding into how many assets the users receive. Otherwise, if this is acceptable to the protocol, be sure to document the behavior so that users are aware.
