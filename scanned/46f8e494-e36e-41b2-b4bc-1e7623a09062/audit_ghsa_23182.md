# [H] Statamic framework Incorrect Permission Assignment 

## Summary
Severity: High
Advisory: GHSA-5m64-9hq5-5pf2
CVE: CVE-2017-11422
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5m64-9hq5-5pf2
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <2.6.0

## Details
Statamic framework before 2.6.0 does not correctly check a session's permissions when the methods from a user's class are called. Problematic methods include reset password, create new account, create new role, etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11422
