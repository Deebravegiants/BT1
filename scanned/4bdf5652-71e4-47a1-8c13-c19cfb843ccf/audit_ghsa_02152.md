# [H] Out of bounds write in serde_cbor

## Summary
Severity: High
Advisory: GHSA-xr7r-88qv-q7hm
CVE: CVE-2019-25001
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-xr7r-88qv-q7hm
Type: github-advisory

## Affected
- crates.io: `serde_cbor` — affected >=0 <0.10.2

## Details
Affected versions of this crate did not properly check if semantic tags were nested excessively during deserialization. This allows an attacker to craft small (< 1 kB) CBOR documents that cause a stack overflow. The flaw was corrected by limiting the allowed number of nested tags.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25001
- https://github.com/pyfisch/cbor/pull/153
- https://github.com/pyfisch/cbor/commit/1aec4f9d71855dbfb223fa61ca60260400cc5d5f
- https://github.com/pyfisch/cbor
- https://github.com/pyfisch/cbor/releases/tag/v0.10.2
- https://rustsec.org/advisories/RUSTSEC-2019-0025.html
