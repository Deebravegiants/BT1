# [H] MJR-1 Incorrect check of timeWindow

## Summary
Severity: High
Contest weight: 0.0088
Dataset id: 6946
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns an incorrect validation of the claim time window in thecontract that governs claim periods. The contract is supposed to enforce a minimum duration of three days for any new claim window that can be set by privileged callers. However, the implemented check compares the supplied _newTimeWindow against the threshold using an inappropriate condition, allowing values that are shorter than the intended three‑day minimum to pass. This logical error originates from a faulty comparison operator or missing boundary condition in the require statement. An attacker who can invoke the function that updates the claim window can therefore set an arbitrarily short window, even zero, which collapses the intended claim period. By shortening the window, the attacker can either prevent legitimate users from submitting claims within the expected timeframe or, if the claim logic permits immediate execution, claim the funds before others have a chance. The impact is that users expecting a three‑day claim period may see their refunds or payouts disappear, balances remain unchanged, or the UI shows a claim window that never actually allows a claim. The bug manifests whenever the function that updates the time window is called, which may be during normal protocol governance or administrative actions. It affects all participants who rely on the claim mechanism, including token holders, claimants, and the protocol itself, because the accounting assumptions about a minimum claim period are violated. The issue was discovered during a formal security audit performed by MixBytes, where the auditors identified that the require statement did not correctly enforce the intended lower bound. Because the check looks syntactically correct, the problem can be subtle and may not be caught by simple testing unless edge‑case windows are exercised. To remediate, the contract should enforce the condition require(_newTimeWindow >= 3 days, "CC: window too short"); ensuring that any new time window is at least three days long, thereby restoring the intended claim period and preventing premature or impossible claim scenarios.

## Recommendation
Change to require(_newTimeWindow >= 3 days, "CC: window too short");
