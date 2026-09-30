# [M] M-15 Weak condition

## Summary
Severity: Medium
Contest weight: 0.0302
Dataset id: 10361
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a weak balance condition that relies on an exact equality comparison of a token balance to decide whether a function may proceed. The contract checks that the token balance of a specific address equals a hard‑coded value using a Comparison.EQUAL operation. Because token balances are mutable and can be altered by any holder of the token, an attacker can change the balance before the check is performed, causing the equality test to fail or succeed unexpectedly. This enables a denial‑of‑service (DoS) scenario: an adversary can transfer tokens into or out of the contract so that the equality condition is never satisfied, causing legitimate calls to revert or be blocked. The impact is that users may be unable to execute expected actions such as withdrawals, trades, or settlements, effectively freezing funds or breaking the protocol’s accounting guarantees. The issue manifests whenever the contract executes the equality‑based balance check, typically during state‑changing operations that depend on a precise token amount. All participants who rely on the contract’s correct accounting – including regular users, liquidity providers, and the protocol itself – are affected because the contract’s logic can be subverted by any token holder. The flaw was discovered during a manual audit that highlighted the unsafe use of Comparison.EQUAL for token balances. It is easy to miss because an equality check looks syntactically correct and may pass tests with static balances, yet it ignores the dynamic nature of ERC‑20 balances. To remediate, the contract should replace the equality comparison with a range or inequality check (e.g., require balance >= expectedAmount) and, where possible, maintain internal accounting that is not directly manipulable by external token transfers. This change restores the intended business logic that a sufficient token amount is present, prevents the DoS vector, and aligns the contract with standard safe‑balance verification patterns.

## Recommendation
We don't recommend using Comparison.EQUAL for token balance checks as it can be easily manipulated.
