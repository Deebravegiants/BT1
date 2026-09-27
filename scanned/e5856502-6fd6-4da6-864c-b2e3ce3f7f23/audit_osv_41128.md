# [M] Mythic < 3.4.0.60 - Unauthorized C2 Profile Configuration Access via Unverified Payload UUID

## Summary
Severity: Medium
Advisory: CVE-2026-57952
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57952
Type: osv

## Details
Mythic before 3.4.0.60 contains an authorization bypass vulnerability in four REST endpoints (c2profile_config_check_webhook, c2profile_redirect_rules_webhook, c2profile_get_ioc_webhook, c2profile_sample_message_webhook) that fail to verify payload ownership. An operator in one operation can invoke these endpoints with a known payload UUID from another operation to access that operation's C2 profile configuration including encryption keys and callback parameters.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57952.json
- https://github.com/its-a-feature/Mythic/releases/tag/v3.4.0.60
- https://nvd.nist.gov/vuln/detail/CVE-2026-57952
- https://www.vulncheck.com/advisories/mythic-unauthorized-c2-profile-configuration-access-via-unverified-payload-uuid
- https://github.com/its-a-feature/Mythic/issues/564
- https://github.com/its-a-feature/Mythic/commit/82648e8241b800a32e1882afc310e7316d98ebaa
- https://github.com/its-a-feature/Mythic
