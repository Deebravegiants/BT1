# [H] Remote code execution in web server context

## Summary
Severity: High
Advisory: GHSA-rhc2-23c2-ww7c
CVE: CVE-2024-37295
CWE: CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-rhc2-23c2-ww7c
Type: github-advisory

## Affected
- Packagist: `aimeos/aimeos-core` — affected >=2024.04.1 <2024.04.5

## Details
### Impact
User with administrative privileges and upload files that look like images but contain PHP code which can then be executed in the context of the web server.

## References
- https://github.com/aimeos/aimeos-core/security/advisories/GHSA-rhc2-23c2-ww7c
- https://nvd.nist.gov/vuln/detail/CVE-2024-37295
- https://github.com/aimeos/aimeos-core
