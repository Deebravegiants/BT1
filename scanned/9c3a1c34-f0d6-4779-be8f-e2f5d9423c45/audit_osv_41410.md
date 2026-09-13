# [H] Bitwarden Server < 2026.6.0 Authorization Bypass via Admin Auth Request

## Summary
Severity: High
Advisory: CVE-2026-60104
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-60104
Type: osv

## Details
Bitwarden Server before 2026.6.0 does not verify that the email in a POST /auth-requests/admin-request body belongs to the authenticated caller, allowing a low-privileged organization member to obtain another user's vault key and a victim-scoped access token by creating a Trusted Device Encryption authentication request, bound to an attacker-controlled public key, that is readable from an unauthenticated endpoint once approved resulting in disclosure of the victim's vault key and account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60104.json
- https://github.com/bitwarden/server/releases#release-v2026.6.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-60104
- https://www.vulncheck.com/advisories/bitwarden-server-authorization-bypass-via-admin-auth-request
- https://github.com/bitwarden/server/pull/7615
- https://github.com/bitwarden/server/commit/dcf4c486b2b5bedecc03a48b427243328cc74a9a
- https://github.com/bitwarden/server
- https://sanjokkarki.com.np/blog/bitwarden-vault-key-heist
