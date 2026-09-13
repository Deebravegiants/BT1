# [M] vibeio-http has a DoS vulnerability in HTTP/1.x chunked encoding parser triggered by maliciously crafted chunk lengths

## Summary
Severity: Medium
Advisory: GHSA-fx4f-mhw4-qm7j
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-fx4f-mhw4-qm7j
Type: github-advisory

## Affected
- crates.io: `vibeio-http` — affected >=0 <0.3.2

## Details
When using the affected versions of the `vibeio-http` crate, an attacker could craft a malicious HTTP/1.x request with a large chunk length (between `usize::MAX - 1` and `usize::MAX` inclusive) and send it, causing the server to crash (integer overflow panic in debug builds, split_to out of bounds panic in release builds).

This was fixed in `vibeio-http` 0.3.2 by erroring on the chunk length if it exceeds `usize::MAX - 2` (using `checked_add()` instead of `+` operator), preventing integer overflow.

## References
- https://github.com/ferronweb/vibeio-http
- https://github.com/ferronweb/vibeio-http/blob/main/CHANGELOG.md#vibeio-http-032
- https://rustsec.org/advisories/RUSTSEC-2026-0181.html
