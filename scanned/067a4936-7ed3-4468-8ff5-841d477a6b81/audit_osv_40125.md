# [H] Hermes WebUI < 0.51.358 Unauthenticated Password Takeover via /api/settings

## Summary
Severity: High
Advisory: CVE-2026-49973
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-49973
Type: osv

## Details
Hermes WebUI before version 0.51.358 contains an improper access control vulnerability that allows unauthenticated remote attackers to hijack initial setup by submitting the _set_password parameter to the settings API endpoint without any network origin restriction. Attackers on any reachable network can send a POST request to the settings endpoint during the first-run setup window to persist an arbitrary password hash, obtain a valid session cookie, and lock out the legitimate operator from their own instance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49973.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.358
- https://nvd.nist.gov/vuln/detail/CVE-2026-49973
- https://www.vulncheck.com/advisories/hermes-webui-unauthenticated-password-takeover-via-api-settings
- https://github.com/nesquena/hermes-webui/pull/3964
- https://github.com/nesquena/hermes-webui/pull/3973
- https://github.com/nesquena/hermes-webui/commit/1126e541325d401538f6a272a9c024c37d47ae08
- https://github.com/nesquena/hermes-webui
