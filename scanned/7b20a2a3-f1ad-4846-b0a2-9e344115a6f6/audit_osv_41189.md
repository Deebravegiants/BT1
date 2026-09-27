# [M] Hermes WebUI < 0.51.521 - Cross-Profile Authorization Bypass via Unset Session Profile on Import

## Summary
Severity: Medium
Advisory: CVE-2026-58174
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58174
Type: osv

## Details
Hermes WebUI before 0.51.521 validates the workspace of an imported session under the active named profile but constructs the Session object without setting its profile in the /api/session/import handler, so the imported session is persisted with a null profile. Because a null profile is treated as the default profile by the profile authorization check, a user on the default profile can export the imported session transcript and use its session identifier to read files from the named profile's workspace, defeating the application's profile isolation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58174.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.521
- https://nvd.nist.gov/vuln/detail/CVE-2026-58174
- https://www.vulncheck.com/advisories/hermes-webui-cross-profile-authorization-bypass-via-unset-session-profile-on-import
- https://github.com/nesquena/hermes-webui/pull/4506
- https://github.com/nesquena/hermes-webui/commit/3d5ef4758e920ba6888d49aaa4341de214693496
- https://github.com/nesquena/hermes-webui
- https://github.com/nesquena/hermes-webui/pull/4489
