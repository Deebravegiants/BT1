# [M] GLOBAL-7 | Cannot Cancel Deposits/Withdrawals

## Summary
Severity: Medium
Contest weight: 0.0386
Dataset id: 17867
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing cancellation mechanism for pending deposit and withdrawal requests. In the contract, when a user initiates a deposit or withdrawal, the request is stored and later executed by a designated keeper. The code does not provide any function that allows the originating user to withdraw the request before the keeper processes it. Consequently, if the keeper fails to execute the request—because of network congestion, gas limits, a bug, or malicious behavior—the user's funds remain locked in the contract with no way to retrieve them. This situation violates the expected business logic that users should retain control over their assets until the operation is completed. The issue was discovered during a systematic audit of the order lifecycle, where the absence of a cancel path was noted. It can be hard to notice because the UI typically shows a pending status and does not display an error, leading users to assume the operation will eventually succeed. The impact is that users lose access to the deposited amount, potentially for an indefinite period, reducing confidence in the protocol and affecting overall liquidity. The problem occurs whenever a deposit or withdrawal request is in the pending state and has not yet been executed by the keeper. Affected parties include any user who relies on the ability to reverse a pending operation and the protocol itself, which may accumulate unrecoverable balances. The bug belongs to the class of stuck‑funds or non‑reversible state transition vulnerabilities, where asynchronous actions lack a user‑initiated rollback. To remediate, the contract should introduce a cancel function that checks the request’s execution status, returns the locked amount to the user, and clears the pending record, thereby restoring the expected invariant that users can always reclaim unprocessed funds.

## Recommendation
Allow users to cancel their deposits and withdrawals and recover their funds.
