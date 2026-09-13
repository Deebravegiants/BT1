# [H] oqs's Post-Quantum Signature scheme Rainbow level I parametersets broken

## Summary
Severity: High
Advisory: GHSA-h864-m8vm-3xvj
Ecosystem: crates.io
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-h864-m8vm-3xvj
Type: github-advisory

## Affected
- crates.io: `oqs` — affected >=0 <0.7.2

## Details
Ward Beullens found a practical key-recovery attack against Rainbow.
The level I parametersets are removed from liboqs starting from version `0.7.2`.
Find the scientific details in [Breaking Rainbow Takes a Weekend on a Laptop](https://eprint.iacr.org/2022/214).

This means all the `oqs::sig::Algorithm::RainbowI*` variants are insecure.

## References
- https://github.com/open-quantum-safe/liboqs-rust
- https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/KFgw5_qCXiI?pli=1
- https://rustsec.org/advisories/RUSTSEC-2022-0047.html
