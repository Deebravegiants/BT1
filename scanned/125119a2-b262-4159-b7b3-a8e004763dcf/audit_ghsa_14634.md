# [H] Borsh serialization of HashMap is non-canonical

## Summary
Severity: High
Advisory: GHSA-wwq9-3cpr-mm53
CWE: CWE-502
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2024-12-04
Source: https://github.com/advisories/GHSA-wwq9-3cpr-mm53
Type: github-advisory

## Affected
- crates.io: `hashbrown` — affected >=0.15.0 <0.15.1

## Details
The borsh serialization of the HashMap did not follow the borsh specification. It potentially produced non-canonical encodings dependent on insertion order. It also did not perform canonicty checks on decoding.

This can result in consensus splits and cause equivalent objects to be considered distinct.

This was patched in 0.15.1.

## References
- https://github.com/rust-lang/hashbrown/issues/576
- https://github.com/kayabaNerve/hashbrown-borsh-poc
- https://github.com/rust-lang/hashbrown
- https://rustsec.org/advisories/RUSTSEC-2024-0402.html
