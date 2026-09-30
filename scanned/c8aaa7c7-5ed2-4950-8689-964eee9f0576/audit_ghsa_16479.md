# [M] matrix-sdk-crypto contains a log exposure of private key of the server-side key backup

## Summary
Severity: Medium
Advisory: GHSA-9ggc-845v-gcgv
CVE: CVE-2024-34353
CWE: CWE-532
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-9ggc-845v-gcgv
Type: github-advisory

## Affected
- crates.io: `matrix-sdk-crypto` — affected >=0.7.0 <0.7.1

## Details
### Introduction

In Matrix, the server-side *key backup* stores encrypted copies of Matrix message keys. This facilitates key sharing between a user's devices and provides a redundant copy in case all devices are lost. The key backup uses asymmetric cryptography, with each server-side key backup assigned a unique public-private key pair.

### Impact

Due to a logic bug introduced in https://github.com/matrix-org/matrix-rust-sdk/pull/2961/commits/71136e44c03c79f80d6d1a2446673bc4d53a2067, the matrix-sdk-crypto crate version 0.7.0 will sometimes log the private part of the backup key pair to Rust debug logs (using the `tracing` crate).

### Patches
This issue has been resolved in matrix-sdk-crypto [version 0.7.1](https://github.com/matrix-org/matrix-rust-sdk/releases/tag/matrix-sdk-crypto-0.7.1).

### Workarounds
None.

### References

- [crates.io release](https://crates.io/crates/matrix-sdk-crypto/0.7.1)

### For more information

If you have any questions or comments about this advisory, please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-rust-sdk/security/advisories/GHSA-9ggc-845v-gcgv
- https://nvd.nist.gov/vuln/detail/CVE-2024-34353
- https://github.com/matrix-org/matrix-rust-sdk/commit/71136e44c03c79f80d6d1a2446673bc4d53a2067
- https://github.com/matrix-org/matrix-rust-sdk/commit/fa10bbb5dd0f9120a51aa1854cec752e25790bb0
- https://github.com/matrix-org/matrix-rust-sdk
- https://github.com/matrix-org/matrix-rust-sdk/releases/tag/matrix-sdk-crypto-0.7.1
