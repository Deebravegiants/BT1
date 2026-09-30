# [C] nimiq-block has skip block quorum bypass via out-of-range BitSet indices & u16 truncation

## Summary
Severity: Critical
Chain: nimiq-block
Component: nimiq-block
CVE: CVE-2026-33471
CWE: Improper Input Validation, Integer Overflow or Wraparound, Insufficient Verification of Data Authenticity, Improper Validation of Specified Quantity in Input
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-6973-8887-87ff
Type: github-advisory

## Details
### Impact
`SkipBlockProof::verify` computes its quorum check using `BitSet.len()`, then iterates `BitSet` indices and casts each `usize` index to `u16` (`slot as u16`) for slot lookup. If an attacker can get a `SkipBlockProof` verified where `MultiSignature.signers` contains out-of-range indices spaced by 65536, these indices inflate `len()` but collide onto the same in-range `u16` slot during aggregation.

This makes it possible for a malicious validator with far fewer than `2f+1` real signer slots to pass skip block proof verification by multiplying a single BLS signature by the same factor.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/pull/3657) is included as part of [v1.3.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0).

### Workarounds
No known workarounds.
