# [M] UB-3 | Report Result Twice

## Summary
Severity: Medium
Contest weight: 0.0368
Dataset id: 16223
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains an idempotency flaw in the function that records the outcome of a betting event. The function does not verify that the event has already been marked as finished before accepting a new result, so it can be called repeatedly. Because the state variable indicating event completion is never checked, an attacker or any caller can invoke the function multiple times, each call overwriting the previously stored winner and loser and triggering the fee‑withdrawal logic again. This allows the treasury fee to be deducted more than once from the same pool of funds and can cause the declared winner to be swapped with the loser, resulting in an incorrect payout distribution. The vulnerability manifests whenever a participant or a malicious actor calls the result‑reporting function after the first successful report, which is typically after the event has logically concluded. Users who expect to receive a single payout based on the true outcome may instead receive nothing, a reduced amount, or an amount that belongs to the opposite side, while the protocol’s treasury may unintentionally collect multiple fees from the same bet. The issue was discovered during a manual audit that examined the state transitions of the betting lifecycle and noticed the absence of a guard such as require(!isEventFinished) before recording the result. Because the contract does not emit an explicit error when the function is called a second time, the problem can be subtle and may only be observed through unexpected balance changes or missing payouts after an event has ended. The bug belongs to the class of missing‑state‑validation or double‑spend vulnerabilities, where a function that should be executed only once can be replayed, breaking accounting assumptions and allowing funds to disappear from users’ balances. To remediate the issue, the contract should enforce a check that the event is not already finished before accepting a new result, making the reporting operation idempotent and preventing repeated fee extraction and outcome swapping.

## Recommendation
Add require(!isEventFinished) in reportResult so a result cannot be reported twice.
