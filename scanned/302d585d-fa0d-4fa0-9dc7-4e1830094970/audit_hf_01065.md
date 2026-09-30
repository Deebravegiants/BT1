# [M] GG-4 | DoS Deposit and Withdraw

## Summary
Severity: Medium
Contest weight: 0.0628
Dataset id: 4052
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because depositing and withdrawing from pool 0 relies on a successful BNB transfer for the dividends payment, it is possible to prevent deposits and withdrawals. If a user were to drain the BNB from the contract using the re-entracy described earlier or the owner drained the BNB using the BNB function, then the call would fail and the transaction would revert.

## Recommendation
Refactor the dividend payments so they are separate from withdrawals and deposits.
