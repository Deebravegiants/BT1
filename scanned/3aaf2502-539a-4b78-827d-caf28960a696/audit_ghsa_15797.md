# [M] matrix-sdk-crypto's `UserIdentity::is_verified` not checking verification status of own user identity while performing the check

## Summary
Severity: Medium
Advisory: GHSA-4qg4-cvh2-crgg
CVE: CVE-2024-40648
CWE: CWE-287, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-18
Source: https://github.com/advisories/GHSA-4qg4-cvh2-crgg
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-crypto` — affected >=0 <0.7.2

## Details
The `UserIdentity::is_verified()` method in the matrix-sdk-crypto crate before version 0.7.2 doesn't take into account the verification status of the user's own identity while performing the check and may as a result return a value contrary to what is implied by its name and documentation.

### Impact

If the method is used to decide whether to perform sensitive operations towards a user identity, a malicious homeserver could manipulate the outcome in order to make the identity appear trusted. This is not a typical usage of the method, which lowers the impact. The method itself is not used inside the `matrix-sdk-crypto` crate.

### Patches

The 0.7.2 release of the `matrix-sdk-crypto` crate includes a fix.

### Workarounds

None.

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-4qg4-cvh2-crgg
- https://nvd.nist.gov/vuln/detail/CVE-2024-40648
- https://github.com/matrix-org/matrix-rust-sdk/commit/76a7052149bb8f722df12da915b3a06d19a6695a
- https://github.com/matrix-org/matrix-rust-sdk
- https://github.com/matrix-org/matrix-rust-sdk/releases/tag/0.7.2-crypto
- https://rustsec.org/advisories/RUSTSEC-2024-0356.html
