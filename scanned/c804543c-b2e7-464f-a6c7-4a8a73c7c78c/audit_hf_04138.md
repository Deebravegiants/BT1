# [H] GLOBAL-1 | Issuance Withdrawals Can Be Trapped

## Summary
Severity: High
Contest weight: 0.1888
Dataset id: 20598
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone may complete a withdrawal that was queued through the Issuance contract by calling the completeWithdraw function on the Vault contract directly. Because the owner is the Issuance address for withdrawals done through the Issuance contract, a user can complete a withdrawal for another user and their funds will be sent to the Issuance contract and stuck. Furthermore, the pendingWithdraws for the true owner will not be updated in the Issuance contract.

## Proof of Concept
https://github.com/GuardianAudits/RestPoCs/commit/a25a9e014c220b28933e32761fbdb7c452196b08#diff-04e502090c72b6a8752f38313a7d0c885bc7f8c222024115a963398b27948bb6

## Recommendation
Refactor the integration between the Issuance contract and the Vault contract such that the pendingWithdraws in the Issuance contract cannot be circumvented.
