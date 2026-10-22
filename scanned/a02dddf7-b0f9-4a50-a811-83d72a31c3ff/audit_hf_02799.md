# [M] Some ETH transfers don't revert if they fail

## Summary
Severity: Medium
Contest weight: 0.0286
Dataset id: 15210
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of ETH transfers that are performed without checking the success flag of the low‑level call, so a failed transfer does not cause the surrounding transaction to revert. This situation occurs in several functions that handle liquidity removal and token exchanges, where the contract attempts to send Ether to a user or another contract using a raw call or an outdated transfer pattern. The root cause is the omission of a require statement or a safe‑send utility after the call, which means that if the recipient contract reverts, runs out of gas, or otherwise refuses the Ether, the call simply returns false and the execution continues. An attacker can trigger such a failure by supplying a malicious contract as the recipient, causing the Ether transfer to fail while the protocol’s internal accounting still records that the user should have received the funds. From the user’s perspective the transaction is reported as successful, the UI shows a completed withdrawal or exchange, but the user’s wallet balance remains unchanged or becomes zero, leading to confusion and the impression that funds have disappeared. The issue is hard to notice because the transaction does not revert and no explicit error is emitted; only a discrepancy between expected and actual balances reveals the problem. Although the bug does not directly enable theft of assets, it expands the attack surface by allowing denial‑of‑service or accounting inconsistencies, which could be leveraged in more complex exploits. The appropriate remediation is to treat the result of every Ether‑sending call as critical: either use OpenZeppelin’s Address.sendValue, which reverts on failure, or explicitly check the returned boolean and revert with a clear error message. By ensuring that any failed ETH transfer aborts the whole operation, the protocol’s accounting invariants are preserved and users receive the funds they expect, restoring confidence in the system.

## Recommendation
Revert if the transfers fails in:
- Curve remove liquidity.
- Curve multi exchange.
- Curve single exchange.
