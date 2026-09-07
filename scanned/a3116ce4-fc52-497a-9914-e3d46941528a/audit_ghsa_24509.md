# [M] MODX Revolution Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-vrw6-7vgj-vj7x
CVE: CVE-2017-9068
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vrw6-7vgj-vj7x
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.5.7

## Details
In MODX Revolution before 2.5.7, an attacker is able to trigger Reflected XSS by injecting payloads into several fields on the setup page, as demonstrated by the database_type parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9068
- https://github.com/modxcms/revolution/pull/13424
- https://citadelo.com/en/2017/04/modx-revolution-cms
- https://github.com/modxcms/revolution
