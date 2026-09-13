# [M] Hermes WebUI < 0.51.443 - Cross-Profile Session Data Exfiltration via Session Export Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-55198
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55198
Type: osv

## Details
Hermes WebUI before 0.51.443 contains an authorization bypass vulnerability in the session export endpoint that allows authenticated users to access sessions from other profiles. The _handle_session_export handler in api/routes.py fails to verify active-profile ownership before serializing session data, enabling attackers to exfiltrate foreign session transcripts by guessing or knowing session identifiers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55198.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.443
- https://nvd.nist.gov/vuln/detail/CVE-2026-55198
- https://www.vulncheck.com/advisories/hermes-webui-cross-profile-session-data-exfiltration-via-session-export-endpoint
- https://github.com/nesquena/hermes-webui/pull/3991
- https://github.com/nesquena/hermes-webui/pull/4269
- https://github.com/nesquena/hermes-webui/commit/2a3baa71b81ca92da8ece8616a09f15894beec71
- https://github.com/nesquena/hermes-webui
