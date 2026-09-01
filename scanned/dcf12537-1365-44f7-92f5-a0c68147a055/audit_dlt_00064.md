# [M] Persistent on-disk corruption of Sapling/Orchard subtree roots after chain fork via pop_tip

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52733
CWE: Incomplete Cleanup, Operation on a Resource after Expiration or Release
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-2gf8-q9rr-jq3h
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node participates in a network where chain forks occur (mainnet, testnet, or any network with multiple miners).

All default configurations are affected. The corruption persists across restarts because it is written to RocksDB.

### Summary

When `pop_tip` removes the tip block during a chain fork, stale Sapling and Orchard note commitment subtree root data is retained in the in-memory non-finalized state. When the chain subsequently finalizes, this stale data is written to the persistent RocksDB state. The corrupted subtree root history affects `z_getsubtreesbyindex` (used by lightwalletd for wallet synchronization) and could affect future chain verification that depends on correct subtree roots.

### Details

The non-finalized state provides two methods for removing blocks: `pop_root` (removes the oldest block during finalization) and `pop_tip` (removes the newest block during a fork revert). `pop_root` correctly cleans up note commitment subtree contributions. `pop_tip` does not: it removes the block but retains the block's subtree root contributions in the in-memory state.

When a chain fork occurs and `pop_tip` reverts the old tip, the winning fork's chain is extended. When that chain is later finalized, the stale subtree data from the reverted blocks is included in the RocksDB write batch and persisted to disk.

The `pop_root`/`pop_tip` asymmetry is specific to subtree root handling. Other state managed by `pop_tip` (nullifiers, UTXOs, anchors, block hashes) uses different cleanup patterns that are not affected.

### Patches

TBD.

The fix adds subtree root cleanup to `pop_tip` matching the pattern already used by `pop_root`.

### Workarounds

There is no configuration-level workaround. Chain forks are natural events on any Proof-of-Work network. Operators can mitigate the downstream impact by periodically verifying subtree root consistency using `z_getsubtreesbyindex` against a known-good reference.

### Impact

Persistent corruption of Sapling and Orchard subtree root history in the RocksDB state database. The corruption survives node restarts. Downstream consumers that rely on `z_getsubtreesbyindex` for wallet synchronization (primarily `lightwalletd` and light wallets) receive incorrect subtree roots. This does not directly affect consensus validation of new blocks but can cause wallet synchronization failures or incorrect wallet state. Recovery requires rebuilding the state database from scratch.

### Credit

Reported by `@dingledropper` via a private GitHub Security Advisory submission.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-2gf8-q9rr-jq3h_
