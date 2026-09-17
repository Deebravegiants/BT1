# [C] Path traversal in mozwire

## Summary
Severity: Critical
Advisory: GHSA-4vhw-4rw7-jfpv
CVE: CVE-2020-35883
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4vhw-4rw7-jfpv
Type: github-advisory

## Affected
- crates.io: `mozwire` — affected >=0 <0.5.0

## Details
An issue was discovered in the mozwire crate through 2020-08-18 for Rust. A ../ directory-traversal situation allows overwriting local files that have .conf at the end of the filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35883
- https://github.com/NilsIrl/MozWire/issues/14
- https://github.com/NilsIrl/MozWire/pull/17/commits/dd0639bf2876773b66382f47285f7db701f628d9
- https://github.com/NilsIrl/MozWire
- https://rustsec.org/advisories/RUSTSEC-2020-0030.html
