# [M] Seerr missing authentication on pushSubscription endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-27792
Aliases: GHSA-gx3h-3jg5-q65f
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27792
Type: osv

## Details
Seerr is an open-source media request and discovery manager for Jellyfin, Plex, and Emby. A missing authorization vulnerability has been identified in the application starting in version 2.7.0 and prior to version 3.1.0. It allows authenticated users to access and modify data belonging to other users. This issue is due to the absence of the `isOwnProfileOrAdmin()` middleware on several push subscription API routes. Version 3.1.0 fixes the issue.

## References
- https://github.com/seerr-team/seerr/releases/tag/v3.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27792.json
- https://github.com/seerr-team/seerr/security/advisories/GHSA-gx3h-3jg5-q65f
- https://nvd.nist.gov/vuln/detail/CVE-2026-27792
- https://github.com/seerr-team/seerr/commit/946bdecec524b4e7f8aaf8f2b3856f319a3580c1
