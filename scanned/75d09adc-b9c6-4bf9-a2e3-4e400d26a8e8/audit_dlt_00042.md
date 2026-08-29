# [M] Far-ahead FindBlocks hashes cause Zebra to ban honest peers that serve requested blocks

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-11
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-qhr3-cvch-5fh2
Type: github-advisory

## Details
| Field | Content |
|---|---|
| Severity | Medium |
| CVSS 3.1 | `AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L` = 4.8 (Medium) |
| Conditional (self-healing / negligible amplification) | Reclassify as hardening; no CVSS in a public issue |
| CWE | CWE-345 (Insufficient Verification of Data Authenticity); secondary CWE-282 (Improper Ownership Management) for the lost source attribution |
| Affected versions | v4.5.0 through v6.2.3 |
| Patched versions | 6.3.0 |
| Reporter | zakura-security |

## Am I affected

You may be affected if all of the following hold:
- You run Zebra v4.5.0 through v6.2.3
- Your node is more than 50,000 blocks behind the network tip, which happens during initial block download or after a long outage.
- Your node accepts inbound peer connections or connects to peers that can answer `FindBlocks`.

A node synced at or near the tip is not affected, because the far-ahead height condition is not met.

## Summary

A connected remote peer can cause a syncing Zebra node to ban honest peers that correctly serve blocks the node itself requested. The attacker returns real, far-ahead block hashes in a `FindBlocks` response. Zebra loses track of which peer supplied those hashes, downloads the blocks from other peers, then penalizes the peer that served each block with enough misbehavior points to ban it. Repeated, this erodes the victim's usable peer set and raises sync disruption and eclipse risk. Consensus rules are not bypassed and far-ahead blocks are still dropped.

## Details

`ObtainTips` sends `FindBlocks` to several peers and accepts each `Response::BlockHashes(Vec<block::Hash>)`. That response type carries no peer address, so the identity of the peer that chose the hashes is discarded.

The returned hashes are downloaded through `BlocksByHash`, which is inventory-routed to a peer that advertised the hash or, failing that, to any ready peer not known to be missing it. This is not necessarily the peer that supplied the `FindBlocks` hashes. When a peer returns a requested block, its connection address is attached to the response as the advertiser.

If the returned block's height is more than 50,000 above the current tip (`VERIFICATION_PIPELINE_DROP_LIMIT`), the download layer returns `AboveLookaheadHeightLimit` carrying that serving-peer address, and the sync component sends 100 misbehavior points to it. The ban threshold is 100, and a previously clean peer reaches it on a single hit, so the serving peer is banned.

The serving peer cannot tell that the request originated from a malicious `FindBlocks` response. It received an exact hash in `getdata` and returned the matching block. The block does not need to be consensus-invalid; a valid block with a coinbase height above the victim's tip plus 50,000 is sufficient.

Verified source (pinned to 4bb9fbd2aab88a22bf3ece3d244c7b58a8b7a5d3; re-pin exact lines before publishing):
- `zebra-network/src/protocol/internal/response.rs`: `BlockHashes(Vec<block::Hash>)` with no source address.
- `zebrad/src/components/sync.rs`: `ObtainTips` fanout of `FindBlocks`; `handle_block_response` sends `(advertiser_addr, 100)` for `AboveLookaheadHeightLimit`.
- `zebra-network/src/peer_set/set.rs`: `route_inv` inventory routing.
- `zebra-network/src/peer/connection.rs`: `InventoryResponse::Available((block, transient_addr))`.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-qhr3-cvch-5fh2_
