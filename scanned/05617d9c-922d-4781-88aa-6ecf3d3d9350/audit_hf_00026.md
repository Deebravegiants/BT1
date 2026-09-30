# [M] QUEUE-2 | Withdrawal Fees Can Be Gamed

## Summary
Severity: Medium
Contest weight: 0.0936
Dataset id: 102
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The accumulated fees from withdrawals during an epoch are distributed to the LP contract after all withdrawals and deposits for that epoch have taken place. This means that the depositors in epoch 10 will receive at least a share of the withdrawal fees from the withdrawals that happened in the same epoch number 10. This way a profit seeking depositor can observe that many withdrawals are queued for the current epoch and queue a deposit right before the epoch ends to collect these withdrawal fees from individuals who withdrew in the same epoch.

## Recommendation
Distribute the withdrawal fees to the depositors who remained in the vault after withdrawals are processed, but before deposits are processed for the current epoch.
