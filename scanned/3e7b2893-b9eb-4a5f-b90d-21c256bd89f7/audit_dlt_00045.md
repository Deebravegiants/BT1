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
5. The `BehindTipHeightLimit` variant does not carry the supplying peer's address (downloads.rs:114-117), unlike `AboveLookaheadHeightLimit`, `InvalidHeight`, and `Invalid`.

In the caller (`zebrad/src/components/sync.rs`, v6.2.0), `BehindTipHeightLimit` is not scored as misbehavior (it falls through the scoring match at sync.rs:1216-1240 into the catch-all), is not added to the re-request set (only `NotFound` is, sync.rs:1249-1265), and is treated as non-fatal (sync.rs:1347-1354). The code comment there assumes the block is genuinely old and the syncer will catch up; that assumption does not hold when the dropped hash is actually the current tip.

Full consensus validation would reject the forged body, both because the V5 coinbase auth digest (which includes the scriptSig) changes the `hashAuthDataRoot` committed in the header, and because the coinbase height would not match the block's real height. Neither check is reached, because the height read and the drop occur first.

Relationship to GHSA-x93j-mj2f-q338 (fixed in v6.2.1): both exploit the same ZIP-244 property, that a body can differ from an honest block while sharing its header hash. They diverge in where the forged body lands. In x93j the body carries a plausible height, reaches semantic verification, is recorded in `SentHashes`, then fails contextual verification, and the stale entry locked out the honest block on the block-known read path until v6.2.1 added a rejected-hash drain there. In this finding the body carries a far-behind height and is dropped at the downloader before semantic verification, so it never enters `SentHashes` and the v6.2.1 drain does not apply. The two are siblings of one family with independent fixes.

## Impact

Discovery of the newest canonical block is delayed for as long as the peer set keeps selecting the attacker to serve that hash. The supplying peer is not penalized, and the hash is not re-requested until the next sync round. For a node that feeds a mining backend, a delayed tip can leave the backend issuing work on an obsolete parent, so hash power spent on that work is at risk of being wasted. The attacker reuses an existing header and performs a cheap body rewrite, with no new proof of work, creating a cost asymmetry against the targeted operator.

Scope limitations: the forged body is not accepted; there is no state corruption and no consensus divergence on the victim node. The effect is transient and self-heals as soon as the peer set selects an honest peer for the hash. Block requests are routed to one peer chosen by power-of-two-choices among peers that advertised the hash, so a lone attacker is selected only intermittently and the node recovers within a round or two. The impact rises when a Sybil set of advertising peers raises the attacker's share of that selection, which is cheap here because a hash-matching-but-invalid response is neither scored nor marked as missing the inventory, so the attacker stays a preferred candidate at no cost. This bites hardest on the freshest tip block, where few honest peers have advertised yet, which is the block a mining backend needs. The remaining question that sets Medium versus High is quantitative: the attacker's per-round selection probability as a function of its advertiser share, and whether a Sybil set sustains mining staleness. A reporter-suggested amplification of fork or re-org attacks is a secondary effect that requires separate assessment and is not relied on here.

## Patches

6.3.0. Recommended fix shape: make the drop decision distinguish a genuinely-old block from a currently-requested near-tip hash whose returned body claims a far-behind height, so that the inconsistency (not the raw behind-tip condition) drives peer scoring and an immediate re-request of the required hash. Carry the supplying peer's address on the relevant path so it can be scored. The change must stay within syncer and peer-scoring policy and must not alter consensus validation, and it must not penalize honest peers that serve legitimately old blocks near a reorg boundary.

## Workarounds

Limited. Peering preferentially with trusted peers reduces exposure to the download race. Mining operators can monitor the age of the parent of issued templates and alert when the tip stops advancing. Neither is a substitute for the fix.

## Credit

zakura-security, reported via an OtterSec engagement on the Zakura fork.

## References

- ZIP-244 (transaction identifiers): https://zips.z.cash/zip-0244
- ZIP-225 (V5 transaction format): https://zips.z.cash/zip-0225
- CWE-345: https://cwe.mitre.org/data/definitions/345.html
- Related advisory (same family, distinct path): GHSA-x93j-mj2f-q338, https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-x93j-mj2f-q338
- Source (pinned v6.2.1): zebrad/src/components/sync/downloads.rs, zebrad/src/components/sync.rs, zebra-chain/src/transaction/txid.rs
