# [H] nimiq-keys: Unchecked Ed25519 signature length in TaggedPublicKey::verify causes remote node panic via DHT

## Summary
Severity: High
Chain: nimiq-keys
Component: nimiq-keys
CVE: CVE-2026-40092
CWE: Unchecked Return Value
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-27w2-87xv-37c6
Type: github-advisory

## Details
### Impact
A malicious network peer can crash any Nimiq full node by publishing a crafted Kademlia DHT record containing a `TaggedSigned<ValidatorRecord, KeyPair>` with a signature field whose byte length is not exactly 64. When the victim node's DHT verifier calls `TaggedSigned::verify`, execution reaches `Ed25519Signature::from_bytes(sig).unwrap()` in the `TaggedPublicKey` implementation for `Ed25519PublicKey`. The `from_bytes` call fails because `ed25519_zebra::Signature::try_from` rejects slices not 64 bytes, and the `unwrap()` panics. The BLS `TaggedPublicKey` implementation correctly returns `false` on error; only the Ed25519 implementation panics.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/pull/3708) is formally released as part of [v1.4.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.4.0).

### Workarounds
No known workarounds.

### Resources
See [PR](https://github.com/nimiq/core-rs-albatross/pull/3708).
