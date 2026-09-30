# [M] M-01 | claimed Value Not Assigned

## Summary
Severity: Medium
Contest weight: 0.0433
Dataset id: 21510
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing state update in the claim routine of the contract. The function is supposed to mark a reward as claimed by setting a boolean flag, but the code never assigns the flag to true. Because the flag remains false, the contract’s internal logic that should prevent further claims never triggers. Consequently any address can invoke the claim function repeatedly, causing the contract to execute the transfer logic multiple times and emit the Claim event each time. This allows an attacker or any user to drain the allocated payout by repeatedly receiving the same amount, effectively making funds disappear from the contract’s balance. The issue manifests whenever a user calls the claim function after the winning condition has been satisfied; there is no guard that checks whether the reward has already been claimed. The problem was identified during a manual audit that inspected the state transitions of the claim flow. It can be hard to notice because the function may appear to succeed – the transfer is performed and the event is emitted – yet the missing assignment is not obvious without tracing the state variable. The bug belongs to the class of “state‑variable not updated” or “missing flag” errors, which break accounting assumptions that each reward can be claimed only once. From a user’s perspective the UI may show that the winner has been paid, but the balance of the contract drops unexpectedly after each claim, and the same winner may receive the payout multiple times. To remediate, the contract should set the claimed flag to true immediately after a successful transfer (or use a modifier that checks and updates the flag atomically) so that subsequent calls are rejected.

## Recommendation
Assign the claimed boolean to true in the claim function.
