# [M] ML-DSA Signature Verification Accepts Signatures with Repeated Hint Indices

## Summary
Severity: Medium
Advisory: GHSA-5x2r-hc65-25f9
CVE: CVE-2026-24850
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-5x2r-hc65-25f9
Type: github-advisory

## Affected
- crates.io: `ml-dsa` — affected >=0.0.4 <0.1.0-rc.4

## Details
**Affected Crate:** `ml-dsa`  
**Affected Versions:** v0.1.0-rc.2 (and commits since `b01c3b7`)  
**Severity:** Medium  
**Reporter:** Oren Yomtov (Fireblocks)

## Summary

The ML-DSA signature verification implementation in the RustCrypto `ml-dsa` crate incorrectly accepts signatures with repeated (duplicate) hint indices. According to the ML-DSA specification (FIPS 204 / RFC 9881), hint indices within each polynomial must be **strictly increasing**. The current implementation uses a non-strict monotonic check (`<=` instead of `<`), allowing duplicate indices.

**Note:** This is a regression bug. The original implementation was correct, but commit `b01c3b7` ("Make ML-DSA signature decoding follow the spec (#895)", fixing issue #894) inadvertently changed the strict `<` comparison to `<=`, introducing the vulnerability.

## Vulnerability Details

### Root Cause

The vulnerability is located in the `monotonic` helper function in `ml-dsa/src/hint.rs`:

```rust
fn monotonic(a: &[usize]) -> bool {
    a.iter().enumerate().all(|(i, x)| i == 0 || a[i - 1] <= *x)
}
```

The comparison operator `<=` allows equal consecutive values, meaning duplicate hint indices are not rejected. The correct implementation should use strict less-than (`<`):

```rust
fn monotonic(a: &[usize]) -> bool {
    a.iter().enumerate().all(|(i, x)| i == 0 || a[i - 1] < *x)
}
```

### Regression Analysis

- **Original correct code** (commit `1d3a1d1` - "Add support for ML-DSA (#877)"): Used `<` (strict)
- **Bug introduced** (commit `b01c3b7` - "Make ML-DSA signature decoding follow the spec (#895)"): Changed to `<=`

The commit message suggests it was intended to fix issue #894 and make decoding follow the spec, but the change to the `monotonic` function was in the wrong direction. The other changes in that commit (to `use_hint` function) may have been correct, but this specific change introduced signature malleability.

### Technical Impact

This vulnerability allows **signature malleability** - the same logical signature can have multiple valid byte-level encodings. An attacker can take a valid signature and create additional "valid" signatures by duplicating hint indices.

Per the ML-DSA specification (FIPS 204, Section 6.2 and Algorithm 26 `HintBitUnpack`), hint indices must be strictly increasing to ensure a unique, canonical encoding. Accepting non-canonical signatures can lead to:

1. **Signature Malleability:** Multiple distinct byte sequences verify as valid for the same message/key pair
2. **Protocol-Level Vulnerabilities:** Systems that rely on signature uniqueness (e.g., for transaction deduplication, replay protection, or signature-based identifiers) may be vulnerable
3. **Interoperability Issues:** Non-compliant signatures may be rejected by other conforming implementations

### Affected Security Levels

All ML-DSA parameter sets are affected:
- ML-DSA-44 (NIST Security Level 2)
- ML-DSA-65 (NIST Security Level 3)
- ML-DSA-87 (NIST Security Level 5)

## Proof of Concept

See the file [`poc_mldsa_repeated_hint.rs`](https://gist.github.com/orenyomtov/fb4616eb77d33017f41a71b30aa41a04) for a standalone proof of concept that demonstrates the vulnerability.

The PoC uses test vectors from the Wycheproof test suite that specifically test for this invalid encoding:

- **Test Vector Source:** [Wycheproof ML-DSA Test Vectors](https://github.com/C2SP/wycheproof/blob/master/testvectors_v1/mldsa_44_verify_test.json)
- Test Case ID 18: "signature with a repeated hint"
- Expected Result: `invalid`
- Actual Result: `valid` (BUG)

## Remediation

Update the `monotonic` function in `ml-dsa/src/hint.rs` to use strict less-than comparison:

```rust
fn monotonic(a: &[usize]) -> bool {
    a.iter().enumerate().all(|(i, x)| i == 0 || a[i - 1] < *x)
}
```

## Design Intent: ML-DSA is NOT Intended to Allow Malleability

While some cryptographic libraries intentionally permit signature malleability for compatibility or performance reasons, **ML-DSA is explicitly designed to prevent it**:

1. **FIPS 204 Specification:** ML-DSA is designed to be strongly unforgeable under chosen message attacks (SUF-CMA). This security property explicitly prevents signature malleability.

2. **NIST PQC Forum Discussion:** In February 2024, there was a discussion on the NIST PQC forum about potential malleability in ML-DSA's hint unpacking. The consensus was that ML-DSA is intended to be SUF-CMA, meaning any malleability issues should be considered bugs and fixed.

3. **No Documentation of Intentional Malleability:** There is no documentation in the RustCrypto `ml-dsa` crate, FIPS 204, or RFC 9881 suggesting that signature malleability is an acceptable or intentional property.

4. **Regression Bug:** The fact that the original implementation had strict ordering (`<`) and this was changed to non-strict (`<=`) in a "fix" commit suggests this was an unintentional regression, not a design decision.

## References
- https://github.com/RustCrypto/signatures/security/advisories/GHSA-5x2r-hc65-25f9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24850
- https://github.com/RustCrypto/signatures/issues/894
- https://github.com/RustCrypto/signatures/pull/895
- https://github.com/RustCrypto/signatures/commit/400961412be2e2ab787942cf30e0a9b66b37a54a
- https://github.com/RustCrypto/signatures/commit/b01c3b73dd08d0094e089aa234f78b6089ec1f38
- https://csrc.nist.gov/pubs/fips/204/final
- https://datatracker.ietf.org/doc/html/rfc9881
- https://github.com/C2SP/wycheproof
- https://github.com/C2SP/wycheproof/blob/master/testvectors_v1/mldsa_44_verify_test.json
- https://github.com/C2SP/wycheproof/blob/master/testvectors_v1/mldsa_65_verify_test.json
- https://github.com/C2SP/wycheproof/blob/master/testvectors_v1/mldsa_87_verify_test.json
- https://github.com/RustCrypto/signatures
