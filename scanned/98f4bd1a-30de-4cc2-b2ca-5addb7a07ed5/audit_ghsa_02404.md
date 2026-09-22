# [C] Out of bounds access in compact_arena

## Summary
Severity: Critical
Advisory: GHSA-7j36-gc4r-9x3r
CVE: CVE-2019-16139
CWE: CWE-125, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7j36-gc4r-9x3r
Type: github-advisory

## Affected
- crates.io: `compact_arena` — affected >=0 <0.4.0

## Details
Affected versions of this crate did not properly implement the generativity, because the invariant lifetimes were not necessarily dropped.

This allows an attacker to mix up two arenas, using indices created from one arena with another one. This might lead to an out-of-bounds read or write access into the memory reserved for the arena.

The flaw was corrected by implementing generativity correctly in version 0.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16139
- https://github.com/llogiq/compact_arena/issues/22
- https://github.com/llogiq/compact_arena
- https://rustsec.org/advisories/RUSTSEC-2019-0015.html
