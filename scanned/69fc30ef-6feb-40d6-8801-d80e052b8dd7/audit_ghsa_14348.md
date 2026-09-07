# [M] Open redirect vulnerability on CMSSecurity relogin screen 

## Summary
Severity: Medium
Advisory: GHSA-fw84-xgm8-9jmv
CVE: CVE-2023-22729
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-fw84-xgm8-9jmv
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <4.12.5

## Details
An attacker can display a link to a third party website on a login screen by convincing a legitimate content author to follow a specially crafted link.

Upgrade to `silverstripe/framework` 4.12.5 or above to remedy the vulnerability.

Reporter: Matthew Dekker

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-fw84-xgm8-9jmv
- https://nvd.nist.gov/vuln/detail/CVE-2023-22729
- https://github.com/silverstripe/silverstripe-framework/commit/1a5bb4cbece1721203977910b8ecd8b79c18dc77
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2023-22729.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/cve-2023-22729
