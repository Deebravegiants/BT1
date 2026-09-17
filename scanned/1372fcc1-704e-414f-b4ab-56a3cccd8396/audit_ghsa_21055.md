# [M] Known v1.3.1 contains Insecure Direct Object Reference

## Summary
Severity: Medium
Advisory: GHSA-4v4p-87m3-5423
CVE: CVE-2022-30852
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-09
Source: https://github.com/advisories/GHSA-4v4p-87m3-5423
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0

## Details
Known v1.3.1 was discovered to contain an Insecure Direct Object Reference (IDOR).

The researcher report indicates that versions 1.3.1 and prior are vulnerable. Version 1.2.2 is the last version tagged on GitHub and in Packagist, and development related to the 1.3.x branch is currently on the `dev` branch of the idno/known repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30852
- https://blog.jitendrapatro.me/multiple-vulnerabilities-in-idno-known-php-cms-software
- https://github.com/idno/known
- https://withknown.com
