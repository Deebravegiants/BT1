# [H] H-01 | withdraw2Contract Crosschain Flow Pays Withdrawal Fee Twice

## Summary
Severity: High
Contest weight: 0.1463
Dataset id: 2211
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the withdraw2Contract crosschain flow, the Ledger credits the fee collector’s account with the withdrawal fee in executeWithdraw2Contract, then credits the same fee again in accountWithDrawFinish. As a result, a single user withdrawal leads to a double fee charge in the Ledger’s accounting, once when the funds are initially frozen and again when the ledger finalizes the withdrawal. This inflates the fee collector’s balance with inexistent funds.

## Recommendation
Remove one of the two fee credits so that the fee is only applied once. For example, either credit the fee collector immediately on executeWithdraw2Contract and avoid doing so in accountWithDrawFinish, or defer the fee credit until final settlement.
