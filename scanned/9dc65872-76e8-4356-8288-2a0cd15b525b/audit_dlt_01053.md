# [M] nimiq-keys: Denial of service in Ed25519 multisig delinearization via invalid curve points

## Summary
Severity: Medium
Chain: nimiq-keys
Component: nimiq-keys
CVE: CVE-2026-46542
CWE: Reachable Assertion
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-h9cc-w26m-j342
Type: github-advisory

## Details
### Impact

A denial-of-service vulnerability exists in the Ed25519 multisig delinearization code path. `Ed25519PublicKey::delinearize()` in `keys/src/multisig/mod.rs` called `.unwrap()` on curve point decompression, which panics when a public key is
constructed from 32 bytes that do not represent a valid point on the Ed25519 curve. `Ed25519PublicKey` construction only validates byte length, not curve membership, so invalid keys can reach the delinearization path and crash the
hosting process.

A secondary panic existed in `Commitment::From<[u8; 32]>`, which similarly called `.unwrap()` on a failing curve point decompression.

**Who is affected:** Browser and desktop wallet users of the web-client WASM library and the `nimiq-wallet` crate, when initiating a multisig operation with an attacker-supplied public key. An attacker must convince the user to include
a crafted public key in a multisig setup — this is not a remotely triggerable node/validator crash.

**Who is NOT affected:** Validator nodes, consensus, blockchain, mempool, and networking code. There is no on-chain multisig account type; multisig is a purely client-side construct, and no validator/consensus code calls the multisig  delinearization path.

### Patches

See [PR](https://github.com/nimiq/core-rs-albatross/pull/3713).

### Workarounds

No code-level workaround exists short of the patch. Users of wallet applications can mitigate exposure by only performing multisig operations with public keys received from trusted sources.

### Resources
- Affected code: `keys/src/multisig/mod.rs`, `keys/src/multisig/commitment.rs`
