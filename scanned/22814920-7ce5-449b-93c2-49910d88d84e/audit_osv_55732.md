# [C] `polymarket-client-sdks` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-p5vf-5754-x7p3
Aliases: RUSTSEC-2026-0011
Ecosystem: crates.io
Published: 2026-02-13
Source: https://osv.dev/vulnerability/GHSA-p5vf-5754-x7p3
Type: osv

## Affected
- crates.io: `polymarket-client-sdks` — affected unspecified

## Details
It appeared to be typosquatting existing crate [`polymarket-client-sdk`](https://crates.io/crates/polymarket-client-sdk) (`sdks` vs `sdk`) and attempting to steal credentials from local files.

The malicious crate had 1 version published on 2026-02-09 and had been downloaded only 33 times. There were no crates depending on this crate on crates.io.

Thanks to Roland Peelen for finding and reporting this to the crates.io team!

## References
- https://rustsec.org/advisories/RUSTSEC-2026-0011.html
