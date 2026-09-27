# [M] Seerr has Broken Object-Level Authorization in User Profile Endpoint that Exposes Third-Party Notification Credentials

## Summary
Severity: Medium
Advisory: CVE-2026-27793
Aliases: GHSA-f7xw-jcqr-57hp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27793
Type: osv

## Details
Seerr is an open-source media request and discovery manager for Jellyfin, Plex, and Emby. Prior to version 3.1.0, the `GET /api/v1/user/:id` endpoint returns the full settings object for any user, including Pushover, Pushbullet, and Telegram credentials, to any authenticated requester regardless of their privilege level. This vulnerability can be exploited alone or combined with the reported unauthenticated account creation vulnerability, CVE-2026-27707. When combined, the two vulnerabilities create a zero-prior-access chain that leaks third-party API credentials for all users, including administrators. Version 3.1.0 contains a fix for both this vulnerability and for CVE-2026-27707.

## References
- https://github.com/seerr-team/seerr/releases/tag/v3.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27793.json
- https://github.com/seerr-team/seerr/security/advisories/GHSA-f7xw-jcqr-57hp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27793
- https://github.com/seerr-team/seerr/commit/4f089b29d0bb41d382168b17aa152eb5b8a25303
