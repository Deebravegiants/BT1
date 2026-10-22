# [H] MJR-5 Possible division by zero

## Summary
Severity: High
Contest weight: 0.0097
Dataset id: 9512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unchecked division operation that can trigger a division‑by‑zero exception in the Lido staking contract. The root cause is a calculation that divides a value representing a user’s stake by the total amount of shares without first verifying that the total shares variable is non‑zero. When the contract’s overall shares balance reaches zero – for example after all participants have withdrawn or a rebase reduces the share count – the denominator becomes zero and the Solidity runtime throws a revert. An attacker or any user can deliberately or unintentionally bring the share total to zero and then invoke the function that performs the division, causing the transaction to fail. This failure can be exploited as a denial‑of‑service vector: legitimate deposits, withdrawals, or reward distributions that rely on the same calculation will revert, preventing users from interacting with the protocol and potentially locking funds in the contract. The impact is that users expect their stake to be calculated and their funds to be transferred, but instead receive no transaction receipt and see no change in balances, effectively experiencing a “funds disappear” symptom because the operation never completes. The condition occurs only in the edge case where the total shares amount equals zero, which is rarely exercised in standard testing, making the bug hard to notice until the edge case is triggered. The issue was discovered by MixBytes during a static analysis audit of the Lido codebase, where the lines performing the division were flagged as potentially unsafe. To remediate, the contract should include a guard that checks the denominator before performing the division and, if the total shares are zero, set the resulting stake to zero or revert with a clear error message. This aligns with the general class of arithmetic‑related vulnerabilities where unchecked division can cause runtime exceptions and break business logic, violating the protocol’s accounting assumptions that a stake must always be derived from a positive share pool.

## Recommendation
We recommend to set a stake to zero if the overall shares amount is equal to zero.
