# [M] nanotar is vulnerable to path traversal in parseTar() and parseTarGzip()

## Summary
Severity: Medium
Advisory: GHSA-92fh-27vv-894w
CVE: CVE-2025-69874
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-92fh-27vv-894w
Type: github-advisory

## Affected
- npm: `nanotar` — affected >=0

## Details
nanotar through 0.2.0 has a path traversal vulnerability in parseTar() and parseTarGzip() that allows remote attackers to write arbitrary files outside the intended extraction directory via a crafted tar archive containing path traversal sequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69874
- https://github.com/EthanKim88/ethan-cve-disclosures/blob/main/CVE-2025-69874-nanotar-Path-Traversal.md
- https://github.com/unjs/nanotar
- https://www.npmjs.com/package/nanotar
