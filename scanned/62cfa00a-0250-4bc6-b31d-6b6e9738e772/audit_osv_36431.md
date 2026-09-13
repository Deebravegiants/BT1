# [H] Rocket.Chat Unauthorized Access to OAuth App Details

## Summary
Severity: High
Advisory: CVE-2026-23477
Aliases: GHSA-g4wm-fg3c-g4p2
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-23477
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. In Rocket.Chat versions up to 6.12.0, the API endpoint GET /api/v1/oauth-apps.get is exposed to any authenticated user, regardless of their role or permissions. This endpoint returns an OAuth application, as long as the user knows its ID, including potentially sensitive fields such as client_id and client_secret. This vulnerability is fixed in 6.12.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23477.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-g4wm-fg3c-g4p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-23477
