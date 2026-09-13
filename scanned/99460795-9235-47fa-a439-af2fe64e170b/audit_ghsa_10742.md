# [M] Roundcube Webmail: Incorrect password comparison in the password plugin

## Summary
Severity: Medium
Advisory: GHSA-46pv-mj2g-93gh
CVE: CVE-2026-35541
CWE: CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-46pv-mj2g-93gh
Type: github-advisory

## Affected
- Packagist: `roundcube/roundcubemail` — affected >=1.7-beta <1.7-rc5

## Details
An issue was discovered in Roundcube Webmail before 1.5.14 and 1.6.14. Incorrect password comparison in the password plugin could lead to type confusion that allows a password change without knowing the old password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35541
- https://github.com/roundcube/roundcubemail/commit/2e6a99b2a38110907ea8d3be8e59ec3d5802c394
- https://github.com/roundcube/roundcubemail/commit/6a275676a8043083c05c961914d830b79e2490d4
- https://github.com/roundcube/roundcubemail/commit/6fa2bddc59b9c9fd31cad4a9e2954a208d793dce
- https://github.com/roundcube/roundcubemail
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.14
- https://github.com/roundcube/roundcubemail/releases/tag/1.7-rc5
- https://roundcube.net/news/2026/03/18/security-updates-1.7-rc5-1.6.14-1.5.14
