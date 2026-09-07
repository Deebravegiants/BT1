# [M] Unbounded memory leak in mempool download pipeline via timeout path cancel_handles retention

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52734
CWE: Missing Release of Memory after Effective Lifetime
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-65jj-fmw8-468q
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your node accepts inbound P2P connections (`network.listen_addr` is set, which is the default).
3. Your node's mempool is active (node is synced near the chain tip).

All default configurations are affected.

### Summary

The mempool download pipeline's `cancel_handles` map retains entries for transactions whose verification times out at the outer `RATE_LIMIT_DELAY` (73-second) boundary. The `tokio::time::error::Elapsed` error carries no payload, so the transaction ID is unrecoverable and the corresponding `cancel_handles` entry (including the full `Gossip::Tx(UnminedTx)`, up to ~2 MB) is never removed. Entries accumulate monotonically with no upper bound or garbage collection, leading to eventual out-of-memory process termination.

### Details

`Downloads::poll_next()` at `zebrad/src/components/mempool/downloads.rs:215-228` handles three terminal states for a verification task:

- `Ok(Ok(...))`: success. Calls `cancel_handles.remove(&tx.transaction.id)`. Correct.
- `Ok(Err(...))`: verification error. Calls `cancel_handles.remove(&hash)`. Correct.
- `Err(elapsed)`: outer timeout. Returns `Err(elapsed)` without removing anything. **Bug.**

`tokio::time::error::Elapsed` has no payload, so the timed-out transaction's `UnminedTxId` is unrecoverable from the error. The consumer at `zebrad/src/components/mempool.rs:663-672` explicitly acknowledges this gap with a TODO comment.

The only cleanup paths for `cancel_handles` are `cancel(mined_ids)` (removes entries matching mined transaction IDs; attacker transactions are never mined) and `cancel_all()` (clears everything on shutdown or chain reset). No periodic GC, no time-based eviction, and no count cap exists.

For direct `tx` pushes (`Gossip::Tx`), the retained entry holds the full deserialized transaction, which can be up to ~9 MB in memory for a transaction near the transparent-output extreme. Per-connection leak rate at worst case: ~685 KB/s (~2.4 GB/hour).

### Patches

The fix preserves the `UnminedTxId` through the timeout error path: wrap the timeout future so the spawned task's outer error carries the txid (e.g., `Err((txid, elapsed))`). In `Downloads::poll_next()`, on the timeout arm, call `cancel_handles.remove(&txid)`.

### Workarounds

There is no configuration-level workaround. Restarting the node clears the accumulated entries. Operators running in memory-constrained environments (containers with cgroup limits) may see the process killed by the OOM killer before natural recovery.

### Impact


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-65jj-fmw8-468q_
