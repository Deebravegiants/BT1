# [C] Permanent Block Discovery Halt via Gossip Queue Saturation and Syncer Poisoning

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-44499
Published: 2026-05-05
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-h9hm-m2xj-4rq9
Type: github-advisory

## Details
## Summary

A composite denial-of-service vulnerability in Zebra's block discovery pipeline allows an unauthenticated remote attacker to permanently halt all new block discovery on a targeted node. The attack exploits three independent weaknesses in the gossip, syncer, and download subsystems — all exercisable from a single TCP connection — to create a monotonically growing block deficit that never self-heals.

## Severity

**Critical** — This is a Denial of Service vulnerability that requires no authentication, no special privileges, and only a single peer connection. The halt is permanent: the node will never recover without operator intervention.

## Affected Versions

All Zebra versions prior to 4.4.0.

## Description

Zebra discovers new blocks through two complementary paths: a gossip path (peers announce blocks via `inv` messages, triggering individual block downloads) and a syncer path (Zebra periodically queries peers with `FindBlocks`/`FindHeaders` to discover chains of missing blocks). Both paths must function for normal operation.

The gossip path was vulnerable because there was no per-connection rate limit on `inv` messages. A single connection could send enough sequential `inv` messages with fake block hashes to fill the entire gossip download queue in under a millisecond. The `FullQueue` return value was silently ignored, so legitimate block announcements from honest peers were dropped with no warning.

The syncer backup path could be degraded by responding with empty `inv` to `FindBlocks` requests and with `NotFound` to block download requests. Both are valid protocol responses that carried zero misbehavior penalty. The attacker's connection was never banned and never disconnected, allowing the degradation to persist indefinitely.

Combining these two vectors, an attacker could suppress both block discovery paths simultaneously from a single connection, causing the node to fall permanently behind the chain tip.

## Impact

**Denial of Service**

* **Attack Vector:** Network, unauthenticated. Requires only a single TCP peer connection.
* **Effect:** Permanent halt of block discovery. The targeted node falls behind the chain tip and never recovers without operator intervention.
* **Scope:** Any Zebra node reachable by the attacker over the peer-to-peer network.

## Fixed Versions

This issue is fixed in Zebra 4.4.0.

The fix drops connections that send empty responses to `FindBlocks` and `FindHeaders` messages, preventing attackers from degrading the syncer path without consequence.

## Mitigation


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-h9hm-m2xj-4rq9_
