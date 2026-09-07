# [M] silverstripe/framework has Cross-site Scripting vulnerability in page name

## Summary
Severity: Medium
Advisory: GHSA-hhvj-mcrx-3vcf
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-hhvj-mcrx-3vcf
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.4
- Packagist: `silverstripe/framework` — affected >=3.5.0-rc1 <3.5.2

## Details
silverstripe/framework is vulnerable to XSS in Page name where the payload `"><svg/onload=alert(/xss/)>` will trigger an XSS alert.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/9574d627f95aca7ae0fcefcae2bf56215777e190
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-001-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-001
