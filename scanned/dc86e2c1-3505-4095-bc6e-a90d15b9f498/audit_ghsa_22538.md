# [H] MODX Revolution blind SQL injection

## Summary
Severity: High
Advisory: GHSA-phhm-6pgm-mxw9
CVE: CVE-2017-1000067
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-phhm-6pgm-mxw9
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=2.0.0 <2.6.0

## Details
MODX Revolution version 2.x - 2.5.6 is vulnerable to blind SQL injection caused by improper sanitization by the escape method resulting in authenticated user accessing database and possibly escalating privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000067
- https://github.com/modxcms/revolution
- https://github.com/modxcms/revolution/blob/2.x/core/xpdo/changelog.txt#L48
- https://github.com/modxcms/revolution/blob/9bf1c6cf7bdc12190b404f93ce7798b39c07bc59/core/xpdo/changelog.txt
