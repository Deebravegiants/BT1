# [C] `sha-rst` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-vgr2-r5hm-f6gf
Aliases: RUSTSEC-2025-0151
Ecosystem: crates.io
Published: 2026-02-12
Source: https://osv.dev/vulnerability/GHSA-vgr2-r5hm-f6gf
Type: osv

## Affected
- crates.io: `sha-rst` — affected unspecified

## Details
This crate was used as a dependency by `finch_cli_rust` and `finch-rst` and contained a malware payload to exfiltrate credentials.

The malicious crate had 1 version published on 2025-12-08 and had been downloaded 22 times. Other than the other crates above that were part of the attack, no other crates depedended on this crate.

Thanks to Matthias Zepper of [NGI Sweden](https://ngisweden.scilifelab.se/) for reporting this to the crates.io team!

## References
- https://rustsec.org/advisories/RUSTSEC-2025-0151.html
