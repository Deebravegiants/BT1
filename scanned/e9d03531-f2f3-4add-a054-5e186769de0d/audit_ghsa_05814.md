# [H] postgres-protocol: Unbounded SCRAM iteration count allows a malicious server to cause CPU-exhaustion denial of service

## Summary
Severity: High
Advisory: GHSA-5x78-73v4-xg6w
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-5x78-73v4-xg6w
Type: github-advisory

## Affected
- crates.io: `postgres-protocol` — affected >=0.3.0 <0.6.12

## Details
A malicious, compromised, or man-in-the-middle server can supply an arbitrarily
large SCRAM-SHA-256 PBKDF2 iteration count during authentication. The client
runs it inline with no upper bound, pinning a `tokio` worker thread for minutes
per connection, possibly stalling the whole async runtime.

Applications that connect only to a trusted database are not exposed; the risk
applies to clients that may connect to untrusted or user-supplied servers, or
whose connection can be intercepted by a man-in-the-middle.

## References
- https://github.com/rust-postgres/rust-postgres/commit/d40097a36a85068ea50a3afbf0ce154ba439e7f0
- https://github.com/rust-postgres/rust-postgres
- https://github.com/rust-postgres/rust-postgres/releases/tag/postgres-protocol-v0.6.12
- https://rustsec.org/advisories/RUSTSEC-2026-0179.html
