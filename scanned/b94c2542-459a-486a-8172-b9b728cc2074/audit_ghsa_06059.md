# [M] postgres-protocol: Panic decoding a malformed `hstore` value allows denial of service

## Summary
Severity: Medium
Advisory: GHSA-rgqc-3x5p-6gwg
CWE: CWE-20, CWE-248
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-rgqc-3x5p-6gwg
Type: github-advisory

## Affected
- crates.io: `postgres-protocol` — affected >=0 <0.6.12

## Details
A malicious or compromised server can return a binary `hstore` value with an
invalid internal length field, causing the client to panic while decoding it.

Applications that connect only to a trusted database are not exposed; the risk
applies to clients that may connect to untrusted or user-supplied servers, or
whose connection can be intercepted by a man-in-the-middle.

## References
- https://github.com/rust-postgres/rust-postgres/commit/a7cf84b5c46431cbca9d8ff50508c23f446efa7d
- https://github.com/rust-postgres/rust-postgres
- https://github.com/rust-postgres/rust-postgres/releases/tag/postgres-protocol-v0.6.12
- https://rustsec.org/advisories/RUSTSEC-2026-0180.html
