# [C] `mysten-metrics` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-g38r-8gmr-ghrf
Aliases: RUSTSEC-2026-0107
Ecosystem: crates.io
Published: 2026-05-04
Source: https://osv.dev/vulnerability/GHSA-g38r-8gmr-ghrf
Type: osv

## Affected
- crates.io: `mysten-metrics` — affected unspecified

## Details
`mysten-metrics` included a build script that attempted to exfiltrate data from the build machine.

The malicious crate had 1 version published on 2026-04-20 and had no evidence of actual usage. This crate had no dependencies on crates.io.

## References
- https://github.com/MystenLabs/sui
- https://rustsec.org/advisories/RUSTSEC-2026-0107.html
