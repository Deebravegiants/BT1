# [H] Code injection in grav

## Summary
Severity: High
Advisory: GHSA-cxgw-r5jg-7xwq
CVE: CVE-2022-2073
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-30
Source: https://github.com/advisories/GHSA-cxgw-r5jg-7xwq
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.34

## Details
Grav is vulnerable to Server Side Template Injection via Twig. According to a previous vulnerability report, Twig should not render dangerous functions by default, such as system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2073
- https://github.com/getgrav/grav/commit/9d6a2dba09fd4e56f5cdfb9a399caea355bfeb83
- https://github.com/getgrav/grav
- https://huntr.dev/bounties/3ef640e6-9e25-4ecb-8ec1-64311d63fe66
