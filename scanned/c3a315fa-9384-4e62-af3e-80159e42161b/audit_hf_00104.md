# [M] M-31 | Remove Pending Position Price Can Be Stale

## Summary
Severity: Medium
Contest weight: 0.0400
Dataset id: 197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the way a smart contract calculates the value of a pending long position that becomes blocked and must be removed. The internal helper function _removeBlockedPendingAction relies on a variable called _lastPrice, which stores the most recent price that was recorded at a previous point in time. Because the function does not query the price oracle or otherwise refresh the price before performing the removal calculation, it may use a stale price that no longer reflects the current market value. This stale‑price usage is a classic instance of a time‑of‑check‑to‑time‑of‑use (TOCTOU) or stale‑data bug, where the contract’s accounting logic is based on outdated information. An attacker or a regular user can trigger the removal of a blocked pending position after a significant price movement. When the contract computes the position’s value with the stale _lastPrice, it may either credit the user with more assets than they are entitled to, or, more commonly, credit them with less, leading to an under‑payment. From the user’s perspective this manifests as a missing or reduced refund: a user expects to receive the value of their open long position after it is cleared, but the amount returned is unexpectedly low or, in edge cases, the balance may even appear to drop to zero. The issue impacts any participant who holds pending positions, the protocol’s accounting accuracy, and ultimately the integrity of funds managed by the contract. It was discovered during a manual audit when the reviewer noticed that the function never updates the price before using it, a logic oversight that is easy to miss because price values are stored internally and not exposed to the UI. The bug is difficult to observe in normal operation because the discrepancy only appears after the price has changed notably and the removal function is called, which may be infrequent. The recommended remediation is to fetch the current market price from the trusted price source at the start of _removeBlockedPendingAction and use that fresh price for all subsequent calculations, ensuring that the protocol’s financial logic always reflects the latest market state. By guaranteeing price freshness, the contract will correctly honor refunds, maintain accurate accounting, and prevent users from experiencing unexpected loss of funds due to stale data.

## Recommendation
Fetch the current price at the beginning of the _removeBlockedPendingAction function.
