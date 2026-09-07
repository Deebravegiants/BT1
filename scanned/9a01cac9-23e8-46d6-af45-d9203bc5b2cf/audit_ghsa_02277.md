# [H] Failure to properly verify ed25519 signatures in libp2p-core

## Summary
Severity: High
Advisory: GHSA-4q4x-67hx-5mpg
CVE: CVE-2019-15545
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4q4x-67hx-5mpg
Type: github-advisory

## Affected
- crates.io: `libp2p-core` — affected >=0 <0.8.1

## Details
Affected versions of this crate did not properly verify ed25519 signatures. Any signature with a correct length was considered valid. This allows an attacker to impersonate any node identity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15545
- https://github.com/libp2p/rust-libp2p
- https://rustsec.org/advisories/RUSTSEC-2019-0004.html
