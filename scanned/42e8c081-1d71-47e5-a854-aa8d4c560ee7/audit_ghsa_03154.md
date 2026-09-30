# [H] Path traversal in servey

## Summary
Severity: High
Advisory: GHSA-v3px-6cc8-f8j3
CVE: CVE-2020-8214
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-v3px-6cc8-f8j3
Type: github-advisory

## Affected
- npm: `servey` — affected >=0 <3.3.2

## Details
A path traversal vulnerability in servey versions prior to 3.3.2 allows an attacker to read content of any arbitrary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8214
- https://hackerone.com/reports/355501
