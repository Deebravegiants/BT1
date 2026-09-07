# [M] MODX Revolution cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7hhg-xj2h-5vq9
CVE: CVE-2017-9070
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7hhg-xj2h-5vq9
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.5.7

## Details
In MODX Revolution before 2.5.7, a user with resource edit permissions can inject an XSS payload into the title of any post via the pagetitle parameter to connectors/index.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9070
- https://github.com/modxcms/revolution/pull/13415
- https://citadelo.com/en/2017/04/modx-revolution-cms
- https://github.com/modxcms/revolution
