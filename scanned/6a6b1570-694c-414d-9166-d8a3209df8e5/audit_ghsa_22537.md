# [H] Grav CMS Cross-Site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-fqff-vcvx-68h3
CVE: CVE-2020-29553
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fqff-vcvx-68h3
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=1.7.0-beta.1
- Packagist: `getgrav/grav` — affected >=0 <1.6.30

## Details
The Scheduler in Grav CMS through 1.7.0-rc.17 allows an attacker to execute a system command by tricking an admin into visiting a malicious website (CSRF).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29553
- https://blog.bssi.fr/cve-2020-29553-cve-2020-29555-cve-2020-29556-multiple-vulnerabilities-within-cms-grav
- https://github.com/getgrav/grav
