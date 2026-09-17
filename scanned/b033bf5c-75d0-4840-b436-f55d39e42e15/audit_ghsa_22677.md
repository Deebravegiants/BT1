# [H] MODX Revolution allows overwriting .htaccess

## Summary
Severity: High
Advisory: GHSA-23gj-x27g-r34f
CVE: CVE-2017-9069
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-23gj-x27g-r34f
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.5.7

## Details
In MODX Revolution before 2.5.7, a user with file upload permissions is able to execute arbitrary code by uploading a file with the name .htaccess.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9069
- https://github.com/modxcms/revolution/pull/13423
- https://citadelo.com/en/2017/04/modx-revolution-cms
- https://github.com/modxcms/revolution
