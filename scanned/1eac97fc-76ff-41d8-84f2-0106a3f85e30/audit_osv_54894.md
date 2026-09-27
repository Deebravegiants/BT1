# [M] CVE-2024-58262

## Summary
Severity: Medium
Advisory: CVE-2024-58262
Aliases: GHSA-x4gp-pqpj-f43q, RUSTSEC-2024-0344
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-27
Source: https://osv.dev/vulnerability/CVE-2024-58262
Type: osv

## Details
The curve25519-dalek crate before 4.1.3 for Rust has a constant-time operation on elliptic curve scalars that is removed by LLVM.

## References
- https://crates.io/crates/curve25519-dalek
- https://rustsec.org/advisories/RUSTSEC-2024-0344.html
- https://github.com/dalek-cryptography/curve25519-dalek/pull/659
