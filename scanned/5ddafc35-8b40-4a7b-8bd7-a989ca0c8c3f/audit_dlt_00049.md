# [M] Potential Chain Stall via stale `parent_error_map`

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8gxx-hc65-vv82
Type: github-advisory

## Details
# Chain stall via stale parent_error_map entry after a poisoned-block rejection

| Field | Value |
|---|---|
| Severity | Moderate |
| CVSS 3.1 | AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (5.9) |
| CWE | CWE-459 (Incomplete Cleanup) / CWE-400 (Uncontrolled Resource Consumption) |
| Affected versions | through v6.0.0 |
| Patched versions | 6.1.0 |
| Reporter credit | @deedim |
| Fix PR | [#10995](https://github.com/ZcashFoundation/zebra/pull/10995) |

## Am I affected?

You are affected if you run an affected version with default peer-to-peer networking. A remote, unauthenticated peer can stall your node at a specific block height for an extended period (on the order of 2,000 blocks, roughly 41 hours, per successful trigger), and can repeat the trigger on each new block to keep the node behind the network tip. The stall clears if you restart the node. There is no crash, no consensus divergence, and no state corruption; the node falls behind the chain tip rather than accepting anything invalid.

## Summary

When a block fails contextual verification, Zebra records its hash in an in-memory map (`parent_error_map`) and propagates that failure to any child block whose parent is in the map. Entries are only removed when the map exceeds a fixed size (2,000 entries) or when the node restarts; an entry is never removed when the canonical block at that hash is later committed successfully. Using the same ZIP-244 coinbase-malleability primitive as GHSA-4m69-67m6-prqp, an attacker can craft a poisoned block whose header hash equals a canonical block N and get it rejected before the canonical N arrives. The poisoned hash then blocks the canonical N+1 from being committed, stalling the node at height N until the stale entry is evicted (after ~2,000 further rejected entries) or the node is restarted.

## Details

Verified on v6.0.0.

The map and its eviction rule (`zebra-state/src/service/write.rs`):

- `PARENT_ERROR_MAP_LIMIT = MAX_BLOCK_REORG_HEIGHT * 2` (write.rs:39). `MAX_BLOCK_REORG_HEIGHT` is 1,000 (`zebra-chain/src/parameters/constants.rs:30`), so the limit is 2,000.
- On a contextual-verification failure the hash is inserted (`parent_error_map.insert(child_hash, error)`, write.rs:409). The only removal is FIFO, and only once the map exceeds the limit: `if parent_error_map.len() > PARENT_ERROR_MAP_LIMIT { ... shift_remove_index(0) }` (write.rs:412-414). There is no removal when the canonical block at that hash later commits.
- If a block's parent hash is already in the map, the child is rejected with the cloned parent error without re-running contextual verification, and the child's own hash is inserted too (write.rs:385-400). So once a poisoned hash is present, the matching canonical block is rejected on arrival and the rejection propagates forward.

The rejection of the poisoned body itself occurs at the auth-data-root check (`block_commitment_is_valid_for_chain_history`, `zebra-state/src/service/check.rs:137`).

Attack sequence: the attacker observes a new block N, constructs a body with the same header hash by mutating the coinbase scriptSig (the ZIP-244 primitive from GHSA-4m69), and delivers it before the canonical N arrives. The poisoned N fails at the auth-data-root check and its hash (equal to the canonical N's hash) is recorded in `parent_error_map`. When the canonical N and N+1 arrive, N+1 is rejected against the stale entry without re-validation, and the node stalls at height N. The stall persists until 2,000 further entries evict the stale one or the node restarts. An attacker can repeat this on each new block to keep the node behind the tip. Triggering requires winning the propagation race against honest peers, the same precondition as GHSA-4m69.

This is a distinct finding from GHSA-4m69. It shares the ZIP-244 primitive and the propagation-race precondition, but it is a different code path (`parent_error_map` eviction, not the SentHashes lockout) with a different effect (a temporary chain stall). Code added around the GHSA-4m69 fix (write.rs:416-431) signals the state service to drop a rejected hash from the sent-hashes set so a re-delivery is not short-circuited; that addresses the sent-hashes lockout but not the `parent_error_map` eviction, so it does not resolve this finding.

## Patches


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8gxx-hc65-vv82_
