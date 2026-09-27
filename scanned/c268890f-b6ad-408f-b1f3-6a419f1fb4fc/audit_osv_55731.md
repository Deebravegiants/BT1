# [C] `time-sync` was removed from crates.io due to malicious code

## Summary
Severity: Critical
Advisory: GHSA-mh23-rw7f-v5pq
Aliases: RUSTSEC-2026-0036
Ecosystem: crates.io
Published: 2026-03-05
Source: https://osv.dev/vulnerability/GHSA-mh23-rw7f-v5pq
Type: osv

## Affected
- crates.io: `time-sync` — affected unspecified

## Details
The `time-sync` crate attempted to exfiltrate `.env` files to a server that was in turn impersonating the legitimate `timeapi.io` service. This the same attack that we've seen three times in the last few days.

The malicious crate had 1 version published on 2026-03-04 approximately 50 minutes before removal and had no evidence of actual downloads. There were no crates depending on this crate on crates.io.

## References
- https://rustsec.org/advisories/RUSTSEC-2026-0036.html
