# [M] Path traversal in apimock's file-serving fallback

## Summary
Severity: Medium
Advisory: RUSTSEC-2026-0276
Aliases: GHSA-72g6-wgrg-vhm7, RUSTSEC-2026-0277
Ecosystem: crates.io
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0276
Type: osv

## Affected
- crates.io: `apimock` — affected >=5.0.0 <5.0.0

## Details
The file-serving fallback joined a request-derived path onto the
configured response directory and checked only that the result existed,
never that it stayed inside that directory. A request containing a raw
`..` segment could read any file readable by the process, returned with
HTTP 200.

Read-only: no write, no code execution.

On the 4.x line `apimock` is a single crate containing the serving code.
Fixed in 4.8.1 by canonicalising each resolved path and rejecting
anything outside its base directory.

**apimock 5.0.0 and later are not affected by this advisory.** From
5.0.0 the serving code moved to the `apimock-server` crate, which
`apimock` depends on; that crate carries its own advisory for the same
issue, fixed in 5.19.1.

## References
- https://crates.io/crates/apimock
- https://rustsec.org/advisories/RUSTSEC-2026-0276.html
- https://github.com/apimokka/apimock-rs/commit/a9c05fec2d36a750c30e797291a0557f230c8faf
