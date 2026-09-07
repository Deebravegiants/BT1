# [M] Silverstripe Framework: Possible XSS attack through media embed

## Summary
Severity: Medium
Advisory: GHSA-gvrw-qqp5-jgc5
CVE: CVE-2026-54720
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-gvrw-qqp5-jgc5
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <6.2.2

## Details
### Impact
The "Insert media from web" functionality in the CMS is vulnerable to XSS from a specially crafted embed.

### Reported by
Jack Wallace from Bastion Security

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-gvrw-qqp5-jgc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54720
- https://github.com/silverstripe/silverstripe-framework/pull/11993
- https://github.com/silverstripe/silverstripe-framework/commit/1bcb02adfc365c6436dc26ab2f6dd32d97f3979b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2026-54720.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://github.com/silverstripe/silverstripe-framework/releases/tag/6.2.2
- https://www.silverstripe.org/download/security-releases/cve-2026-54720
