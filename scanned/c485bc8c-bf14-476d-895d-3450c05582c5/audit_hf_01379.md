# [M] M-2 Possible DoS of exchange_received

## Summary
Severity: Medium
Contest weight: 0.0259
Dataset id: 7095
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service condition in the exchange_received routine of a Curve StableSwap meta‑pool implementation. The routine validates the amount of base‑pool token received (dx) with a strict equality check, requiring dx to be exactly equal to the expected amount. Because the check uses a literal equality (dx == expected) instead of allowing a greater‑than‑or‑equal comparison, an attacker can exploit rounding or minimal‑transfer edge cases. By sending a single wei of any base‑pool token directly to the meta‑pool contract, the equality condition fails, causing the function to revert. This revert blocks subsequent calls to the exchange function, effectively freezing swaps for all users. The impact is that legitimate traders and liquidity providers are unable to perform exchanges, leading to a loss of functionality and potential loss of confidence in the protocol. The condition only manifests when an abnormal, tiny token transfer is made to the pool, a scenario that is not covered by normal usage patterns and therefore may go unnoticed during standard testing. The issue was discovered during a manual code audit by MixBytes, who identified the strict check at line 389 of CurveStableSwapMetaNG.vy. The problem is subtle because the failure only occurs with an atypical input (1 wei), making it easy to miss in functional tests. To remediate, the equality check should be relaxed to a greater‑than‑or‑equal comparison (dx >= expected) or the logic should be rewritten to handle minimal‑transfer cases without reverting, thereby preventing the DoS vector while preserving the intended accounting guarantees.

## Recommendation
We recommend changing the strict check dx == dx to dx >= dx.
