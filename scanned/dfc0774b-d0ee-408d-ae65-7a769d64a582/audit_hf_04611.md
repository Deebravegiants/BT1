# [M] M-10 | Vault Whitelist Can Be Set One Above Max

## Summary
Severity: Medium
Contest weight: 0.0414
Dataset id: 22216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an off‑by‑one boundary error in the function that adds new vault addresses to the protocol’s whitelist. The contract checks the current number of whitelisted vaults against a configured maximum using a "less‑than‑or‑equal" comparison (<= maxVaults). Because the check allows equality, an additional vault can be inserted after the limit has already been reached, effectively permitting one vault more than the intended cap. This occurs whenever the setVaultWhitelist routine is called after the whitelist length equals the maximum value. The root cause is the incorrect relational operator in the require statement, which does not enforce the strict upper bound required by the business rule. An attacker or a careless administrator can exploit this by submitting a transaction that adds a vault after the limit is hit, thereby bypassing the intended restriction. The impact is that the protocol may host more vault contracts than it was designed to manage, potentially leading to resource exhaustion, unexpected fee distribution, or the inclusion of malicious vaults that can siphon funds or disrupt accounting. Users may notice an extra vault appearing in the UI, see their expected list of approved vaults longer than advertised, or experience unexpected behavior when interacting with the newly added vault. The issue was discovered during a manual audit that examined the whitelist management logic and identified the relational operator mismatch. Because the condition only fails when the whitelist length exceeds the maximum by more than one, the bug can remain hidden during normal operation until the limit is reached and an extra vault is added, making it difficult to spot without targeted testing. To remediate, the require statement should enforce a strict less‑than comparison (require(_vaultWhitelistAry.length < maxVaults, ...)), ensuring that the whitelist never exceeds the configured ceiling. This correction aligns the implementation with the intended business rule that the number of whitelisted vaults must never surpass the maximum allowed, restoring proper accounting and preventing unauthorized vault inclusion.

## Recommendation
Change from require(_vaultWhitelistAry.length <= maxVaults, 'M'); to require(_vaultWhitelistAry.length < maxVaults, 'M');
