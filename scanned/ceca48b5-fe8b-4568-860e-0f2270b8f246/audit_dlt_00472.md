# [H] nimiq-blockchain: Validity store off by one error

## Summary
Severity: High
Chain: nimiq-blockchain
Component: nimiq-blockchain
CVE: CVE-2026-46369
CWE: Off-by-one Error, Authentication Bypass by Capture-replay
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-3763-qp59-59vf
Type: github-advisory

## Details
### Impact
The validity store treats a transaction with stored `block_number = X` as "in window" only when `X > last_bn - transaction_validity_window_blocks` (strict inequality). However the protocol's `Transaction::is_valid_at` accepts a transaction for inclusion in any block in `[validity_start_height - blocks_per_batch, validity_start_height + window - 1]`. By choosing `validity_start_height = X + blocks_per_batch` (the largest value still compatible with first inclusion at block X), an attacker can replay the same signed transaction in any block B such that `X + window < B < validity_start_height + window`, i.e., a contiguous window of `blocks_per_batch - 1` blocks (59 on MainNet, ~10 minutes) during which the replay-protection check fails to flag it. The same transaction is then executed twice: the sender is debited twice, the recipient credited twice.

### Patches
https://github.com/nimiq/core-rs-albatross/pull/3772

### Workarounds
No known workarounds
