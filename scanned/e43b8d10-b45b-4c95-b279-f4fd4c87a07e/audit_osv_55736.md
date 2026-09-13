# [C] `time_calibrators` was removed from crates.io due to malicious code

## Summary
Severity: Critical
Advisory: GHSA-wf45-3gpw-vrqv
Aliases: RUSTSEC-2026-0031
Ecosystem: crates.io
Published: 2026-03-04
Source: https://osv.dev/vulnerability/GHSA-wf45-3gpw-vrqv
Type: osv

## Affected
- crates.io: `time_calibrators` — affected unspecified

## Details
The `time_calibrators` crate attempted to exfiltrate `.env` files to a server that was in turn impersonating the legitimate `timeapi.io` service.

The malicious crate had 1 version published on 2026-03-03 approximately 3 hours before removal and had no evidence of actual downloads. There were no crates depending on this crate on crates.io.

Rust security response working group thanks cybergeek for finding and reporting this, and thanks to Emily Albini for co-ordinating with the crates.io team.

## References
- https://github.com/suntea279491/time_calibrator
- https://rustsec.org/advisories/RUSTSEC-2026-0031.html
