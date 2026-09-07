# [H] ureport arbitrary file read vulnerability

## Summary
Severity: High
Advisory: GHSA-9vfc-qxc8-wrpq
CVE: CVE-2023-48848
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-9vfc-qxc8-wrpq
Type: github-advisory

## Affected
- Maven: `com.bstek.ureport:ureport2-core` — affected >=0

## Details
An arbitrary file read vulnerability in ureport v2.2.9 allows a remote attacker to arbitrarily read files on the server by inserting a crafted path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48848
- https://github.com/h00klod0er/ureport2-vuln
- https://github.com/youseries/ureport
