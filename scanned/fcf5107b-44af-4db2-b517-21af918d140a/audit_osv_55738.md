# [C] `dnp3times` was removed from crates.io due to malicious code

## Summary
Severity: Critical
Advisory: GHSA-xhw7-jhmp-j62j
Aliases: RUSTSEC-2026-0032
Ecosystem: crates.io
Published: 2026-03-05
Source: https://osv.dev/vulnerability/GHSA-xhw7-jhmp-j62j
Type: osv

## Affected
- crates.io: `dnp3times` — affected unspecified

## Details
The `dnp3times` crate attempted to exfiltrate `.env` files to a server that was in turn impersonating the legitimate `timeapi.io` service. It was loosely trying to typosquat the `dnp3time` crate, but otherwise was the same attack as the recent `time_calibrator` and `time_calibrators` malware.

The malicious crate had 1 version published on 2026-03-04 approximately 6 hours before removal and had no evidence of actual downloads. There were no crates depending on this crate on crates.io.

## References
- https://rustsec.org/advisories/RUSTSEC-2026-0032.html
