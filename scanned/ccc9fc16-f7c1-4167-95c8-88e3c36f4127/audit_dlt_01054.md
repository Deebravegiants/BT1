# [M] nimiq-primitives: BlockInclusionProof interlink issue when hops are empty

## Summary
Severity: Medium
Chain: nimiq-primitives
Component: nimiq-primitives
CVE: CVE-2026-46539
CWE: Insufficient Verification of Data Authenticity
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-799f-29jm-gr6c
Type: github-advisory

## Details
### Impact
A logic flaw in `BlockInclusionProof::is_block_proven` causes the function to return true without performing any cryptographic verification when `get_interlink_hops` yields an empty hop list. This occurs when the target block is at the election block position immediately preceding the election head's epoch. An attacker providing transaction inclusion proofs can forge a MacroBlock header for that epoch position and have it accepted as "proven" without any hash or signature verification.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/pull/3705) is formally released as part of [v1.4.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.4.0).

### Workarounds
No Workarounds

### Resources
See [PR](https://github.com/nimiq/core-rs-albatross/pull/3705).
