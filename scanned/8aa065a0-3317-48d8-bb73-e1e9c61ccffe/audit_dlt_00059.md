# [M] Valid one-hash FindBlocks response discarded, causing false close-to-tip status and a false /ready result while behind the chain tip

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-h8m8-844p-v3m9
Type: github-advisory

## Details
# Valid one-hash FindBlocks response discarded, causing false close-to-tip status and a false /ready result while behind the chain tip

| Field | Value |
|---|---|
| Severity | Medium |
| CVSS 3.1 | 5.3 (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`)|
| CWE | CWE-754: Improper Check for Unusual or Exceptional Conditions |
| Affected versions | Releases through v6.2.3 |
| Patched versions | v6.3.0 |
| Reporter credit | See Credit |
| GHSA | GHSA-h8m8-844p-v3m9 |
| Fix PR | ZcashFoundation/zebra#11165 |

## Am I affected

You are affected if all of the following hold:

- You run a Zebra node on a release up to and including v6.2.3, on mainnet or testnet (default configuration; no non-default flags required).
- Your node is at or near the chain tip during normal operation.
- You rely on the `/ready` health endpoint (for load balancing, traffic routing, monitoring, or mining readiness), or on any feature gated by close-to-tip status.

An affected node can report ready while it is still up to `ready_max_blocks_behind` blocks (default 2) behind the network tip. Upgrade to v6.3.0.

## Summary

A Zebra node can report itself ready while it is still behind the chain tip. When a peer returns a valid one-hash `FindBlocks` response that contains the node's next block, the syncer discards that hash, downloads no block, and records a zero-length sync sample. The zero-length sample makes `SyncStatus::is_close_to_tip()` return true, and the `/ready` endpoint then returns `200 OK` while the node is one or two blocks behind. The impact is a liveness and status-correctness defect: a node can silently stay behind the tip while dependent infrastructure treats it as ready. The issue is fixed in v6.3.0.

## Details

The syncer requires at least two unknown hashes before it acts on a `FindBlocks` response, so a valid one-hash response produces no download.

In `ChainSync::obtain_tips` (`zebrad/src/components/sync.rs:747`), Zebra requests hashes after its current block locator. On mainnet and testnet a one-hash response is discarded: older releases strip the final hash before the download decision, and v6.2.3 discards the response when the unknown-hash slice does not contain a two-element chunk, logging "discarding response that extends only one block" and continuing (`sync.rs:831-838`). Either path yields the same outcome for a valid one-hash response that advertises the node's next block: no `BlocksByHash` download is queued.

At the end of `obtain_tips`, Zebra records the number of newly queued downloads, which is zero in this case (`sync.rs:889`, `push_obtain_tips_length(new_downloads)`).

`SyncStatus::is_close_to_tip` (`zebrad/src/components/sync/status.rs:74`) averages recent sync-length samples and returns true when the average is below `MIN_DIST_FROM_TIP`, which is 20 (`status.rs:28`, comparison at `status.rs:94-98`). A single zero-length sample is enough to satisfy this.

The false close-to-tip status is externally visible through the readiness endpoint. `ready` (`zebrad/src/components/health.rs:221`) returns `SERVICE_UNAVAILABLE` with "syncing" unless `is_close_to_tip()` holds (`health.rs:236`), then returns `200 OK` when the estimated remaining block count is within `ready_max_blocks_behind`. The default `ready_max_blocks_behind` is 2, which is exactly the range where a peer can legitimately return a short response containing only the next block hash.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-h8m8-844p-v3m9_
