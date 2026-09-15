# [H] Vikunja 0.22.0 through 2.3.0 Authentication Bypass via Principal ID Collision

## Summary
Severity: High
Advisory: CVE-2026-68581
Aliases: GHSA-vvcv-vpph-h844
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-68581
Type: osv

## Details
Vikunja versions 0.22.0 through 2.3.0 fail to validate the principal type in API token management. Because user IDs and link-share IDs are independent numeric sequences and both resolve through a generic web.Auth.GetID() interface, a link-share JWT whose numeric ID equals a target user's ID is treated as that user by the /api/v1/tokens endpoints. An authenticated attacker can obtain a target's numeric user ID via authenticated user search, then create link shares on an attacker-writable project until the link-share sequence reaches that value, and use the resulting link-share JWT to list, create, and delete the target user's API tokens (including issuing a new token with attacker-chosen scopes under the target's permissions). Fixed in version 2.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68581.json
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-vvcv-vpph-h844
- https://nvd.nist.gov/vuln/detail/CVE-2026-68581
- https://www.vulncheck.com/advisories/vikunja-through-authentication-bypass-via-principal-id-collision
- https://github.com/go-vikunja/vikunja/commit/95b7e673fb5ee407498fa4b13e8b4c57847a4a0b
- https://github.com/go-vikunja/vikunja/commit/e6b25bd57b537ef9a72b5acdadf446ca5ef77bfa
