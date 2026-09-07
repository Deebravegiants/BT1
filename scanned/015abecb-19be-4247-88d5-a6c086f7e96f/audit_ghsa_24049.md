# [M] Grav CMS Local File Injection

## Summary
Severity: Medium
Advisory: GHSA-r3rg-jrjq-w4mr
CVE: CVE-2020-29556
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r3rg-jrjq-w4mr
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=1.7.0-beta.1
- Packagist: `getgrav/grav` — affected >=0 <1.6.30

## Details
The Backup functionality in Grav CMS through 1.7.0-rc.17 allows an authenticated attacker to read arbitrary local files on the underlying server by exploiting a path-traversal technique. (This vulnerability can also be exploited by an unauthenticated attacker due to a lack of CSRF protection.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29556
- https://blog.bssi.fr/cve-2020-29553-cve-2020-29555-cve-2020-29556-multiple-vulnerabilities-within-cms-grav
- https://github.com/getgrav/grav
