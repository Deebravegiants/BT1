# [M] NU5+ block-body poisoning via the `bad-blk-length` rejection path

## Summary
Severity: Medium
Chain: Zcash
Component: zcash/zcash
Published: 2026-07-13
Source: https://github.com/zcash/zcash/security/advisories/GHSA-382w-958v-m5jr
Type: github-advisory

## Details
## Summary

This is another case of the same class of vulns as GHSA-qvwc-hc2r-82qv (`bad-blk-sigops`) and GHSA-wmwc-773c-qcvv (`bad-cb-length`), due to an incomplete fix for GHSA-rpcw-q5mr-gq35.

A peer that can construct any block close to `MAX_BLOCK_SIZE` for the same NU5+ header that an honest miner has produced, can pad v5 `scriptSig` bytes to push the serialized body over `MAX_BLOCK_SIZE`. This is authorizing data, not committed to by `hashMerkleRoot`. The malformed body is rejected as a `bad-blk-length` failure with `corruptionPossible = false`. As in the similar bugs referenced above, the shared `CBlockIndex` entry is marked `BLOCK_FAILED_VALID`, and the genuine body for the same header is subsequently rejected as `duplicate-invalid`.

## Severity

Same Moderate severity as the other bugs in this class. I'm a node maintainer so I'm not eligible for a bounty. The impact is per-node consensus divergence: any node that ingests the malformed body before the genuine body becomes unable to accept the genuine body for that height without restart. Other nodes that received the genuine body first continue normally.

## Affected versions

All zcashd versions that activated NU5 and did not yet include zodl-inc/zcash-security-fixes#163.

- The vector exists from NU5 activation onward, since it only relies on v5 `scriptSig` being authorizing data.
- The same fix scope as GHSA-qvwc-hc2r-82qv applies — versions exposed are those where `bad-blk-length` is reached inside `CheckBlock` with `corruptionPossible = false` on the active-tip path.

## Attack shape

The details are almost identical to GHSA-qvwc-hc2r-82qv, just the particular failure exploited is different. The comprehensive approach in the last consensus commit of zodl-inc/zcash-security-fixes#163 (or equivalent) is needed to fix it.

`bad-blk-length` fires from this check in `CheckBlock()`:

```cpp
if (block.vtx.empty()
    || block.vtx.size() > MAX_BLOCK_SIZE
    || ::GetSerializeSize(block, SER_NETWORK, PROTOCOL_VERSION) > MAX_BLOCK_SIZE) {
    return state.DoS(100, error("CheckBlock(): size limits failed"),
                     REJECT_INVALID, "bad-blk-length");
}
```

The third disjunct, `GetSerializeSize(block) > MAX_BLOCK_SIZE`, is the body-mutable one: the serialized block byte-length includes every v5 `scriptSig` byte. An attacker can:

1. Take a genuine NU5+ block whose body is close to but under `MAX_BLOCK_SIZE`.
2. Pad arbitrary bytes into a non-coinbase v5 transparent input's `scriptSig`. The padded `scriptSig` is in `auth_digest`, so the tx's `txid_digest` is unchanged; the Merkle root over the body's txids and the header's `hashMerkleRoot` field is unchanged; therefore the header hash is unchanged.
3. Submit the malformed body for the genuine header.

On a victim node that ingests the malformed body before the genuine one:

1. `CheckBlock()` runs. `hashMerkleRoot` is verified (passes — `txid_digest` is preserved). Then the size limit is checked: `GetSerializeSize(block) > MAX_BLOCK_SIZE` — fails.
2. `state.DoS(100, ..., "bad-blk-length")` is called. Without the fix in zcash-security-fixes#163, no `BodyCorruption::Possible` argument is passed, so `corruptionPossible = false`. (Just the second consensus commit on zcash-security-fixes#163 is not sufficient; that will fix the active-tip path but not the sidechain path.)
3. `AcceptBlock()` propagates the rejection with `corruptionIn = false`. The shared `CBlockIndex` for this header is marked `BLOCK_FAILED_VALID`.
4. The genuine body for the same header now arrives. The header's `CBlockIndex` is already `BLOCK_FAILED_VALID`, so the block is rejected with `duplicate-invalid` without re-running `CheckBlock()` on the genuine body.

The honest header is now permanently not-acceptable on the victim node until restart with the `BLOCK_FAILED_VALID` bit cleared.

## Feasibility

The honest block being attacked is more constrained than for `bad-blk-sigops` (GHSA-qvwc-hc2r-82qv). The sigops vector needs only ~1 KB of `OP_CHECKMULTISIG` padding to push `nSigOps > 20000`; the size vector needs enough padding to push the serialized body across the ~2 MB `MAX_BLOCK_SIZE` boundary from whatever length the honest block has. Most mainnet blocks run well under the limit, so the attacker needs to target a block that is already close.

The vector becomes more reliable when blocks are full or near-full — periods of high transaction backlog raise the success rate. The attacker also chooses *when* to fire, so they can wait for a near-full period rather than attempting on every block.

## Fix

Two complementary mechanisms:

1. **Per-call classification.** Pass `corruptionIn = true` (or `BodyCorruption::Possible`) to the `state.DoS(...)` call on the `bad-blk-length` path. This is a direct analogue of the `bad-blk-sigops` fix in the first commit of zcash-security-fixes#163.
2. **Structural classification via commitment tracking.** The third consensus commit in #163's tracks the two header-to-body commitments (`hashMerkleRootChecked` and `hashBlockCommitmentsChecked`) on `CValidationState`. Body-derived rejections classified as `BodyCorruption::Default` automatically resolve to `corruptionPossible = true` whenever the body is not yet fully pinned by both commitments. With this mechanism in place, `bad-blk-length` is classified correctly even without the explicit `BodyCorruption::Possible` annotation — though I suggest retaining the explicit annotation for clarity and defence in depth.

The structural fix (mechanism 2) closes the general class of body-poisoning vulnerabilities. Any future `CheckBlock()`-stage rejection on an authdata-bound field inherits the correct classification by default.

## Workarounds

Operators of nodes that experience a stuck header can restart the node with `-reindex` to clear cached `BLOCK_FAILED_VALID` flags, but this is recovery rather than mitigation.

## References

- **GHSA-qvwc-hc2r-82qv**: NU5 block body poisoning via `bad-blk-sigops` — the same denial-of-service shape routed through sigop count.
- **GHSA-rpcw-q5mr-gq35**: original NU5 body-poisoning advisory — the predecessor of which GHSA-qvwc / GHSA-wmwc and this advisory are completions.
- **GHSA-wmwc-773c-qcvv**: related advisory also closed by zcash-security-fixes#163.
- **ZIP 244**: defines the `txid_digest` / `auth_digest` split for v5 transactions and `hashBlockCommitments` / `hashAuthDataRoot` for blocks.

## Credit

Identified during an audit of all `state.DoS` call sites while working on zcash-security-fixes#163, after the `bad-blk-sigops` analogue had been fixed and the broader `CheckBlock()` site classification was being reviewed for completeness.

🤖 Generated with [Claude Code (Opus 4.7, 1M context)](https://claude.com/claude-code)
