# [M] `pnet_packet` buffer overrun in `set_payload` setters

## Summary
Severity: Medium
Advisory: GHSA-cf4g-fcf8-3cr9
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-02-09
Source: https://github.com/advisories/GHSA-cf4g-fcf8-3cr9
Type: github-advisory

## Affected
- crates.io: `pnet_packet` — affected >=0 <0.27.2

## Details
As indicated by this [issue](https://github.com/libpnet/libpnet/issues/449#issuecomment-663355987), a buffer overrun is possible in the `set_payload` setter of the various mutable "Packet" struct setters. The offending `set_payload` functions were defined within the struct `impl` blocks in earlier versions of the package, and later by the `packet` macro.

Fixed in the `packet` macro by [this](https://github.com/libpnet/libpnet/pull/455) PR.

## References
- https://github.com/libpnet/libpnet/issues/449
- https://github.com/libpnet/libpnet
- https://rustsec.org/advisories/RUSTSEC-2020-0167.html
