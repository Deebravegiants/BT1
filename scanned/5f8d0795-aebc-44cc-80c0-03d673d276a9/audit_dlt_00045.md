# [H] Coinbase scriptSig rewrite drops a required block during sync without penalizing the supplying peer

## Summary
Severity: High
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-11
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-g95h-hw6g-pvgv
Type: github-advisory

## Details
# Coinbase scriptSig rewrite drops a required block during sync without penalizing the supplying peer

| Field | Content |
|---|---|
| Severity | High |
| CVSS 3.1 | `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` |
| CWE | CWE-345 (Insufficient Verification of Data Authenticity); secondary CWE-349 (Acceptance of Extraneous Untrusted Data With Trusted Data) |
| Affected versions | <=6.2.3|
| Patched versions | 6.3.0 |
| Reporter credit | zakura-security, via an OtterSec engagement on the Zakura fork |
| GHSA | GHSA-g95h-hw6g-pvgv |

## Am I affected

You are affected if all of the following hold:
- You run an affected Zebra version.
- Your node syncs from the public P2P network (the default).
- Your node has at least one inbound or outbound peer that can respond to your block-download requests (the normal case).

The impact is materially higher if your node supplies chain state or block templates to a miner or pool. No non-default configuration is required.

Upgrading to v6.2.1 does not remediate this specific path. v6.2.1 fixed a related but distinct issue (GHSA-x93j-mj2f-q338, a SentHashes lockout on the block-known read path); the download path described here is unchanged in v6.2.1.

## Summary

A malicious peer can delay your node's discovery of the newest canonical block by answering a block-download request with a forged body that still matches the requested block hash. The peer copies a real block, rewrites only the coinbase transaction scriptSig to encode height 1, and keeps the original header. Because the coinbase scriptSig is excluded from the V5 transaction ID, the merkle root and block hash are unchanged, so the response passes the hash check. The syncer then reads the forged height from the unvalidated body, treats the block as too far behind the tip, and drops it before consensus validation runs. The supplying peer is not scored or banned, and the required hash is not re-requested immediately; the node waits for the next sync round (roughly 10 seconds) to rediscover it. The peer set selects one peer per request from those that advertised the hash, so an attacker that advertises the tip and answers cheaply stays a preferred candidate and can repeat this.

## Details

For V5+ transactions the transaction ID follows ZIP-244 and excludes authorizing data, including the transparent input scriptSig. The block's transaction merkle tree is built from these transaction IDs.

An attacker copies a canonical block with hash H, changes only the coinbase scriptSig to encode height 1 instead of the real height, and retains the original header. The resulting body keeps the canonical merkle root and, because the header is unchanged, the canonical block hash H and proof of work.

In the syncer's download path (`zebrad/src/components/sync/downloads.rs`, v6.2.0):
1. The response for the requested hash is accepted; the block hash matches H.
2. The coinbase height is read from the unverified body (downloads.rs:446).
3. Because the forged height is more than `MAX_BLOCK_REORG_HEIGHT` behind the tip, the path returns `BehindTipHeightLimit` (downloads.rs:505-516).
4. This return happens before the verifier is called (downloads.rs:520+), so consensus never validates the body.

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-g95h-hw6g-pvgv_
