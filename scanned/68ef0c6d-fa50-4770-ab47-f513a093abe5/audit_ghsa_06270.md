# [M] tokio-postgres: Panic on a `DataRow` with fewer fields than columns allows denial of service

## Summary
Severity: Medium
Advisory: GHSA-3gjw-f78c-vvpw
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-3gjw-f78c-vvpw
Type: github-advisory

## Affected
- crates.io: `tokio-postgres` — affected >=0.4.0 <0.7.18

## Details
A malicious or compromised server can send a row containing fewer fields than
its row description declares columns. Reading one of the missing columns then
panics with an out-of-bounds index, aborting the calling task. This affects even
the otherwise non-panicking `try_get`, and both `Row` and `SimpleQueryRow`.

Applications that connect only to a trusted database are not exposed; the risk
applies to clients that may connect to untrusted or user-supplied servers, or
whose connection can be intercepted by a man-in-the-middle.

## References
- https://github.com/rust-postgres/rust-postgres/commit/7a00ffa9ad4d951ec0a4564b52f1780fa9d353c1
- https://github.com/rust-postgres/rust-postgres
- https://github.com/rust-postgres/rust-postgres/releases/tag/tokio-postgres-v0.7.18
- https://rustsec.org/advisories/RUSTSEC-2026-0178.html
