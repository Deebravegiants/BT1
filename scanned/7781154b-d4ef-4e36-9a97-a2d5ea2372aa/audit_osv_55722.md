# [C] `finch_cli_rust` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-6v2j-vr4h-f632
Aliases: RUSTSEC-2025-0152
Ecosystem: crates.io
Published: 2026-02-12
Source: https://osv.dev/vulnerability/GHSA-6v2j-vr4h-f632
Type: osv

## Affected
- crates.io: `finch_cli_rust` — affected unspecified

## Details
This attempts to typosquat the existing crate [`finch_cli`](https://crates.io/crates/finch_cli) to steal credentials from local files.

The malicious crate had 1 version published on 2025-12-08 and had been downloaded 18 times. There were no crates depending on this crate on crates.io.

Thanks to Matthias Zepper of [NGI Sweden](https://ngisweden.scilifelab.se/) for reporting this to the crates.io team!

## References
- https://rustsec.org/advisories/RUSTSEC-2025-0152.html
