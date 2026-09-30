# [M] Hermes WebUI < 0.51.443 - Broken Access Control in /api/session Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-55197
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55197
Type: osv

## Details
Hermes WebUI before 0.51.443 contains a broken access control vulnerability in the /api/session endpoint that allows authenticated users to disclose cross-profile session transcripts. Attackers can bypass profile boundary checks by directly querying session IDs belonging to other profiles via GET /api/session?session_id=<foreign_id>&messages=1 to retrieve unauthorized conversation transcripts and metadata.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55197.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.443
- https://nvd.nist.gov/vuln/detail/CVE-2026-55197
- https://www.vulncheck.com/advisories/hermes-webui-broken-access-control-in-api-session-endpoint
- https://github.com/nesquena/hermes-webui/pull/3982
- https://github.com/nesquena/hermes-webui/pull/4269
- https://github.com/nesquena/hermes-webui/commit/2a3baa71b81ca92da8ece8616a09f15894beec71
- https://github.com/nesquena/hermes-webui
