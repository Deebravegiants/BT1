# [C] `finch-rst` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-xp79-9mxw-878j
Aliases: RUSTSEC-2025-0150
Ecosystem: crates.io
Published: 2026-02-12
Source: https://osv.dev/vulnerability/GHSA-xp79-9mxw-878j
Type: osv

## Affected
- crates.io: `finch-rst` — affected unspecified

## Details
This attempts to typosquat the existing crate [`finch`](https://crates.io/crates/finch) to steal credentials from local files.

The malicious crate had 1 version published on 2025-12-08 and had been downloaded 21 times. There were no crates depending on this crate on crates.io.

Thanks to Matthias Zepper of [NGI Sweden](https://ngisweden.scilifelab.se/) for reporting this to the crates.io team!

## References
- https://rustsec.org/advisories/RUSTSEC-2025-0150.html
