# [H] ISU-1 | Tokens Stolen When Completing Withdraw

## Summary
Severity: High
Contest weight: 0.1596
Dataset id: 20600
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Issuance contract was created to facilitate early buyouts of pending withdraws. The function completeWithdraw must be called after a withdraw has matured from a queued state. This function incorrectly sends the funds to the caller of the function, rather than the owner of the pending withdraw. This makes it possible for anyone to call this function, with any non-pending withdraw and steal the funds.

## Proof of Concept
https://github.com/GuardianAudits/RestPoCs/pull/6/files#diff-099e0009dc3141fc29142a78b6be9eeca78f19cd95ce3ffb9c706f38fa517428

## Recommendation
Validate that the owner of the withdrawal is the msg.sender.
