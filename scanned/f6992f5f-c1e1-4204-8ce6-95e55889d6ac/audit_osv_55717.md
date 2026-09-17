# [C] `polymarket-clients-sdk` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-382q-fpqh-29f7
Aliases: RUSTSEC-2026-0010
Ecosystem: crates.io
Published: 2026-02-06
Source: https://osv.dev/vulnerability/GHSA-382q-fpqh-29f7
Type: osv

## Affected
- crates.io: `polymarket-clients-sdk` — affected unspecified

## Details
It appeared to be typosquatting existing crate [`polymarket-client-sdk`](https://crates.io/crates/polymarket-client-sdk) (`clients` vs `client`) and attempting to steal credentials from local files.

The malicious crate had 6 versions published on 2026-02-05 and had been downloaded only 59 times. There were no crates depending on this crate on crates.io.

Polymarket thanks [Socket.dev](https://socket.dev/) for detecting and reporting this to the crates.io team!

## References
- https://github.com/Polymarket/rs-clob-client
- https://rustsec.org/advisories/RUSTSEC-2026-0010.html
