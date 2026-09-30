# [M] ISU-7 | Pending Withdrawals Can Be Bought When Eigen Is Paused

## Summary
Severity: Medium
Contest weight: 0.1025
Dataset id: 20587
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users that queue their withdraw on EigenLayer using the Issuance contract can have their withdrawals taken over by others as long as they are paid the equivalent withdraw amount in exchange. This mechanism leaves a potential abuse situation when EigenLayer has withdrawal completion paused (PAUSED_EXIT_WITHDRAWAL_QUEUE) so that nobody would be able to call completeQueuedWithdrawal at that time. During this time, users of the Issuance contract can take ownership of withdrawals that, unbeknown to them, can't be finalized at that time, basically buying into a blocked position.

## Recommendation
Do not allow changing the owner of pending withdrawals if EigenLayer has withdrawal completion paused. Checking that withdrawal completion is paused can be done by calling the Pausable.paused(uint8) method with the PAUSED_EXIT_WITHDRAWAL_QUEUE(2) value.
