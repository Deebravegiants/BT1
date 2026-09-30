# [H] MODX Revolution Directory Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-cgrv-6h2h-6f7v
CVE: CVE-2017-9067
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cgrv-6h2h-6f7v
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.5.7

## Details
In MODX Revolution before 2.5.7, when PHP 5.3.3 is used, an attacker is able to include and execute arbitrary files on the web server due to insufficient validation of the action parameter to setup/index.php, aka directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9067
- https://github.com/modxcms/revolution/pull/13422
- https://github.com/modxcms/revolution/pull/13428
- https://citadelo.com/en/2017/04/modx-revolution-cms
- https://github.com/modxcms/revolution
