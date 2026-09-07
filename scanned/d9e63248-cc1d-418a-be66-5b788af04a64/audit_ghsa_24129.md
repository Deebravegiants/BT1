# [M] Silverstripe Flash Clipboard Reflected XSS

## Summary
Severity: Medium
Advisory: GHSA-rfvw-5848-gxc5
CVE: CVE-2019-12205
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rfvw-5848-gxc5
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.0.0 <4.3.5
- Packagist: `silverstripe/admin` — affected >=0 <1.3.5
- Packagist: `silverstripe/framework` — affected >=4.4.0-rc1 <4.4.4

## Details
SilverStripe versions 3.0.0 until 4.3.5 and 4.4.4 are vulnerable to Flash Clipboard Reflected XSS. Versions 4.3.5 and 4.4.4 of `silverstripe/framework` and version 1.3.5 of `silverstripe/admin` contain a fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12205
- https://github.com/silverstripe/silverstripe-admin/commit/6e6fa5c618b9dbf4cc0a56704834bfa1d5b0d18e
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2019-12205.yaml
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/CVE-2019-12205
- https://www.silverstripe.org/download/security-releases/cve-2019-12205
