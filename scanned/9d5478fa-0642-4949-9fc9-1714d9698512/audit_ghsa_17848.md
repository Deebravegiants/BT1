# [M] matrix-sdk-crypto missing facility to signal rotation of a verified cryptographic identity

## Summary
Severity: Medium
Advisory: GHSA-r5vf-wf4h-82gg
CVE: CVE-2024-52813
CWE: CWE-223, CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-07
Source: https://github.com/advisories/GHSA-r5vf-wf4h-82gg
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-crypto` — affected >=0 <0.8.0

## Details
### Impact

Versions of the matrix-sdk-crypto Rust crate before 0.8.0 lack a dedicated mechanism to notify that a user's cryptographic identity has changed from a verified to an unverified one, which could cause client applications relying on the SDK to overlook such changes.

### Patches

matrix-sdk-crypto 0.8.0 adds a new `VerificationLevel::VerificationViolation` enum variant which indicates that a previously verified identity has been changed.

### References

- Patch: https://github.com/matrix-org/matrix-rust-sdk/pull/3795

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-r5vf-wf4h-82gg
- https://nvd.nist.gov/vuln/detail/CVE-2024-52813
- https://github.com/matrix-org/matrix-rust-sdk/pull/3795
- https://github.com/matrix-org/matrix-rust-sdk
- https://rustsec.org/advisories/RUSTSEC-2024-0434.html
