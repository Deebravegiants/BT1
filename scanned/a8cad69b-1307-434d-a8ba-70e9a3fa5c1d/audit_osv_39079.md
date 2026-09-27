# [H] Bitwarden Server < 2026.4.1 Authentication Bypass via SCIM API Key

## Summary
Severity: High
Advisory: CVE-2026-43640
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43640
Type: osv

## Details
Bitwarden Server prior to v2026.4.1 does not require master-password re-authentication when retrieving or rotating an organization's SCIM API key, allowing an authenticated user with SCIM management privileges to obtain the key using only a valid session.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43640.json
- https://github.com/bitwarden/server/releases/tag/v2026.4.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-43640
- https://www.vulncheck.com/advisories/bitwarden-server-authentication-bypass-via-scim-api-key
- https://github.com/bitwarden/server/pull/7403
- https://github.com/bitwarden/server/commit/eb251d9bf80724c87b187661783b9354d1784083
- https://github.com/bitwarden/server
- https://sanjokkarki.com.np/blog/bitwarden-scim-key-bypass
