# [M] Reliance on Cookies without Validation and Integrity Checking in getgrav/grav

## Summary
Severity: Medium
Advisory: GHSA-cg3q-59w7-rvc2
CVE: CVE-2021-3818
CWE: CWE-565
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-cg3q-59w7-rvc2
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.21

## Details
grav is vulnerable to Reliance on Cookies without Validation and Integrity Checking. A cookie with an overly broad path can be accessed through other applications on the same domain. Since cookies often carry sensitive information such as session identifiers, sharing cookies across applications can lead a vulnerability in one application to cause a compromise in another.

## References
- https://github.com/getgrav/grav/commit/c51fb1779b83f620c0b6f3548d4a96322b55df07
- https://github.com/getgrav/grav
- https://huntr.dev/bounties/c2bc65af-7b93-4020-886e-8cdaeb0a58ea
