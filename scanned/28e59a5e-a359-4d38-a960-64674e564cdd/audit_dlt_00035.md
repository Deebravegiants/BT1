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


_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-382w-958v-m5jr_
