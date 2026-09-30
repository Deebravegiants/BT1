# [M] Panic in mp3-metadata due to the lack of bounds checking

## Summary
Severity: Medium
Advisory: GHSA-927q-g9w9-pm54
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-927q-g9w9-pm54
Type: github-advisory

## Affected
- crates.io: `mp3-metadata` — affected >=0 <0.4.0

## Details
The `get_id3()` methods used by `mp3_metadata::read_from_slice()` does not perform adequate bounds checking when recreating the tag due to the use of desynchronization.

Fixed in [Fix index error](https://github.com/GuillaumeGomez/mp3-metadata/pull/37), released as part of 0.4.0.

## References
- https://github.com/GuillaumeGomez/mp3-metadata/issues/36
- https://github.com/GuillaumeGomez/mp3-metadata/pull/37
- https://github.com/GuillaumeGomez/mp3-metadata
- https://rustsec.org/advisories/RUSTSEC-2025-0027.html
