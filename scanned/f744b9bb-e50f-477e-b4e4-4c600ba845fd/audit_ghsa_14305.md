# [M] Missing permission check of canView in GridFieldPrintButton

## Summary
Severity: Medium
Advisory: GHSA-jh3w-6jp2-vqqm
CVE: CVE-2023-22728
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-jh3w-6jp2-vqqm
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <4.12.5

## Details
The GridField print view incorrectly validates the permission of DataObjects potentially allowing a content author to view records they are not authorised to access. 

Upgrade to `silverstripe/framework` 4.12.5 or above to address the issue.

Reported by Stephan Bauer from [relaxt Webdienstleistungsagentur GmbH](https://www.relaxt.at/)

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-jh3w-6jp2-vqqm
- https://nvd.nist.gov/vuln/detail/CVE-2023-22728
- https://github.com/silverstripe/silverstripe-framework/commit/fd5d8217e83768d7bf841e94b2d4d82642d5bc58
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2023-22728.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/cve-2023-22728
