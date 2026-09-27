# [H] SQL Injection in Fork CMS

## Summary
Severity: High
Advisory: GHSA-q863-cchm-c6c6
CVE: CVE-2022-0153
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-25
Source: https://github.com/advisories/GHSA-q863-cchm-c6c6
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.11.1

## Details
Fork CMS contains a SQL injection vulnerability in versions prior to version 5.11.1. When deleting submissions which belong to a formular (made with module `FormBuilder`), the parameter `id[]` is vulnerable to SQL injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0153
- https://github.com/forkcms/forkcms/commit/7a12046a67ae5d8cf04face3ee75e55f03a1a608
- https://github.com/forkcms/forkcms
- https://huntr.dev/bounties/841503dd-311c-470a-a8ec-d4579b3274eb
