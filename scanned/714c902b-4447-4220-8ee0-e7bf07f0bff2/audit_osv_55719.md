# [C] `tracing-check` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-5pmp-jpcf-pwx6
Aliases: RUSTSEC-2026-0019
Ecosystem: crates.io
Published: 2026-03-02
Source: https://osv.dev/vulnerability/GHSA-5pmp-jpcf-pwx6
Type: osv

## Affected
- crates.io: `tracing-check` — affected unspecified

## Details
This is part of an ongoing campaign to attempt to typosquat crates in the [`polymarket-client-sdk`](https://crates.io/crates/polymarket-client-sdk) ecosystem to exfiltrate user credentials.

The malicious crate had 1 version published on 2026-02-24 approximately 4 hours before removal and had no evidence of actual downloads. There were no crates depending on this crate on crates.io.

The crates.io team advises anyone developing with Polymarket to review dependencies carefully. We are investigating ways to mitigate this attacker who appears to be very motivated to steal Polymarket credentials.

## References
- https://github.com/polymarket/rs-clob-client
- https://rustsec.org/advisories/RUSTSEC-2026-0019.html
