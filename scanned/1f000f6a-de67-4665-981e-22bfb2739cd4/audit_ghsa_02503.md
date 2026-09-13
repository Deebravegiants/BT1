# [C] Out of bounds write in prost

## Summary
Severity: Critical
Advisory: GHSA-gv73-9mwv-fwgq
CVE: CVE-2020-35858
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gv73-9mwv-fwgq
Type: github-advisory

## Affected
- crates.io: `prost` — affected >=0 <0.6.1

## Details
Affected versions of this crate contained a bug in which decoding untrusted input could overflow the stack. On architectures with stack probes (like x86), this can be used for denial of service attacks, while on architectures without stack probes (like ARM) overflowing the stack is unsound and can result in potential memory corruption (or even RCE).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35858
- https://github.com/danburkert/prost/issues/267
- https://github.com/danburkert/prost/commit/04091d3e745c27590a5f1b7f581793e4159486b5
- https://github.com/danburkert/prost
- https://rustsec.org/advisories/RUSTSEC-2020-0002.html
