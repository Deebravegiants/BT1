# [C] `exploration` was removed from crates.io for malicious code

## Summary
Severity: Critical
Advisory: GHSA-99j7-fhr2-xfj4
Aliases: RUSTSEC-2026-0155
Ecosystem: crates.io
Published: 2026-07-10
Source: https://osv.dev/vulnerability/GHSA-99j7-fhr2-xfj4
Type: osv

## Affected
- crates.io: `exploration` — affected unspecified

## Details
A method within the `exploration` crate attempted to download and execute a payload from a remote site.

The malicious crate had 1 version published on 2026-06-02, approximately 1 hour before removal, and had no evidence of actual usage. This crate had no dependencies on crates.io.

Rustsec to Kirill Boychenko from the [Socket Threat Research Team](https://socket.dev/) for reporting this crate.

## References
- https://rustsec.org/advisories/RUSTSEC-2026-0155.html
