# [M] silverstripe/versioned has XSS in archive admin restore

## Summary
Severity: Medium
Advisory: GHSA-m4g4-86qc-v8w7
CVE: CVE-2026-55779
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-m4g4-86qc-v8w7
Type: github-advisory

## Affected
- Packagist: `silverstripe/versioned` — affected >=0 <3.2.1

## Details
### Impact
It's possible to use the page title as an XSS vector when restoring a page in ArchiveAdmin

### Reporter
Steve Boyd
Silverstripe Ltd.

## References
- https://github.com/silverstripe/silverstripe-versioned/security/advisories/GHSA-m4g4-86qc-v8w7
- https://github.com/silverstripe/silverstripe-versioned/pull/541
- https://github.com/silverstripe/silverstripe-versioned/commit/6e30a2cf8d4b9233690464da61bd0fc4d3e92952
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/versioned/CVE-2026-55779.yaml
- https://github.com/silverstripe/silverstripe-versioned
- https://github.com/silverstripe/silverstripe-versioned/releases/tag/3.2.1
- https://www.silverstripe.org/download/security-releases/cve-2026-55779
