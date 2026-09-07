# [C] Uninitialized memory access in outer_cgi

## Summary
Severity: Critical
Advisory: GHSA-6vmq-jh76-hq43
CVE: CVE-2021-30454
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-6vmq-jh76-hq43
Type: github-advisory

## Affected
- crates.io: `outer_cgi` — affected >=0 <0.2.1

## Details
An issue was discovered in the outer_cgi crate before 0.2.1 for Rust. A user-provided Read instance receives an uninitialized memory buffer from KeyValueReader.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30454
- https://github.com/SolraBizna/outer_cgi/issues/1
- https://github.com/SolraBizna/outer_cgi/commit/dd59b3066e616a08e756f72de8dc3ab11b7036c4
- https://github.com/SolraBizna/outer_cgi
- https://rustsec.org/advisories/RUSTSEC-2021-0051.html
