# [M] oqs's Post-Quantum Key Encapsulation Mechanism SIKE broken

## Summary
Severity: Medium
Advisory: GHSA-hrjv-pf36-jpmr
Ecosystem: crates.io
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-hrjv-pf36-jpmr
Type: github-advisory

## Affected
- crates.io: `oqs` — affected >=0 <0.7.2

## Details
Wouter Castryck and Thomas Decru presented an efficient key recovery attack on the SIDH protocol.
As a result, the secret key of SIKEp751 can be recovered in a matter of hours.
The SIKE and SIDH schemes will be removed from oqs 0.7.2.

[An efficient key recovery attack on SIDH (preliminary version)](https://eprint.iacr.org/2022/975)

## References
- https://github.com/open-quantum-safe/liboqs-rust/pull/151
- https://github.com/open-quantum-safe/liboqs-rust
- https://rustsec.org/advisories/RUSTSEC-2022-0045.html
