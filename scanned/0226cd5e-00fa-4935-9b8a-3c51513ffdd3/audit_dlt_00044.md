# [M] Poisoned blocks can delay download of valid blocks (SentHashes lockout on the KnownBlock path)

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-22
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-x93j-mj2f-q338
Type: github-advisory

## Details
# Poisoned blocks can delay download of valid blocks (SentHashes lockout on the KnownBlock path)

| Field | Content |
|---|---|
| Severity | Medium  |
| CVSS 3.1 | AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L = 5.3 (Medium). Conditional High: A:H = 7.5 |
| CWE | CWE-459 Incomplete Cleanup |
| Affected versions | All releases prior to v6.2.1 |
| Patched version | v6.2.1 |
| Reporter credit | oxarbitrage (GitHub) |

## Am I affected
You are affected if you run a Zebra release earlier than v6.2.1 with the default configuration. No custom configuration, RPC access, or authentication is required for the attack. Upgrade to v6.2.1 to remediate. Restarting the node also clears the condition, because the affected state is held in memory only.

## Summary
A connected peer can delay a node's block download and hold it one block behind the network tip. The peer sends a block that shares an honest block's header hash but fails contextual verification. After Zebra rejects that block, the rejected hash stays recorded as "sent," and the node's later "is this block already known" check reports the honest block as present. The node then skips downloading the honest body. The condition persists until unrelated commit activity clears the stale entry or the node restarts. It does not crash the node, corrupt state, or cause a consensus disagreement.

## Details
When Zebra sends a semantically verified block to the non-finalized write task, it records the block hash in `non_finalized_block_write_sent_hashes` (`SentHashes`) to prevent the same block from being queued twice while contextual verification is pending.

If contextual verification rejects the block, the write task returns the hash on a rejected-hash channel (`zebra-state/src/service/write.rs`), and `drain_non_finalized_rejected_hashes()` (`zebra-state/src/service.rs`) removes it from `SentHashes`. Before v6.2.1 that drain ran on the commit path (`queue_and_commit_to_non_finalized_state`) and on the `AwaitUtxo` path, but not on the `Request::KnownBlock` path. `Request::KnownBlock` called `known_sent_hash()`, which reads `SentHashes.contains(hash)` directly, so a stale rejected entry reported the block as present.

ZIP-244 permits a block body that differs from an honest block while sharing the same header hash. An attacker sends a contextually invalid body first. Zebra rejects it, leaving the shared hash stale in `SentHashes`. Sync then reaches the same hash and calls `Request::KnownBlock` before downloading the honest body (`zebrad/src/components/sync.rs` `state_contains`, and `zebrad/src/components/inbound/downloads.rs`). The stale entry makes both callers treat the honest block as already present, so Zebra does not download it.

The stale entry clears only as a side effect of another block reaching the commit path. At the network tip there may be no child block to trigger that cleanup, so the node can remain unable to obtain the honest block until unrelated commit activity occurs or the node restarts.

## Impact
An unauthenticated peer can keep a default-configuration node one block behind the tip by repeating the attack. The impact is bounded: the node continues to operate, the affected state is in memory and clears on restart, and there is no crash, state corruption, or consensus divergence. Whether the node can be held persistently unable to reach the tip (rather than lagging transiently) depends on sync retry behavior at the tip and is being confirmed; the severity above is provisional pending that confirmation.

## Patches
Fixed in v6.2.1. The `Request::KnownBlock` handler now drains pending rejected hashes before checking `SentHashes`, so a rejected same-hash block no longer locks out the honest block on the read path. This completes the earlier remediation of the SentHashes rejected-entry lockout, which had covered the commit path but not this read path.

## Workarounds
Upgrade to v6.2.1. If you cannot upgrade immediately, restarting the node clears the condition, though it can recur under continued attack.

## Credit
Reported by jvff.


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-x93j-mj2f-q338_
