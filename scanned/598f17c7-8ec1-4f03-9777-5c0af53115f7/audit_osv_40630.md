# [H] Hermes WebUI < 0.51.368 - Profile-Scoped Authorization Bypass via Forged hermes_profile Cookie

## Summary
Severity: High
Advisory: CVE-2026-53871
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-53871
Type: osv

## Details
Hermes WebUI before 0.51.368 contains an authorization bypass vulnerability in the get_profile_cookie() function that accepts unauthenticated profile names from the hermes_profile cookie. An authenticated attacker can forge the hermes_profile cookie value to bypass profile-scoped authorization checks and access sessions, files, and resources across different profiles.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53871.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.368
- https://nvd.nist.gov/vuln/detail/CVE-2026-53871
- https://www.vulncheck.com/advisories/hermes-webui-profile-scoped-authorization-bypass-via-forged-hermes-profile-cookie
- https://github.com/nesquena/hermes-webui/pull/4023
- https://github.com/nesquena/hermes-webui/pull/4036
- https://github.com/nesquena/hermes-webui/commit/9e96f5f6adf93b6d1e27ebddfb4d2833ca06ff3b
- https://github.com/nesquena/hermes-webui
