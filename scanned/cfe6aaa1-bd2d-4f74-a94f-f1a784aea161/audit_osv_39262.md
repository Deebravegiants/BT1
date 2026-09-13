# [C] Empty API_TOKEN disables authentication on network-reachable HTTP/SSE transport

## Summary
Severity: Critical
Advisory: CVE-2026-44830
Aliases: GHSA-crr4-xrj9-ww8g
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44830
Type: osv

## Details
Nocturne Memory is a lightweight, rollbackable, and visual Long-Term Memory Server for MCP Agents. Prior to 2.4.1, when API_TOKEN is unset or empty, the BearerTokenAuthMiddleware bypasses authentication for all HTTP requests. Combined with the default 0.0.0.0 host binding and CORS allow_origins=["*"], operators following the Docker setup without explicitly setting API_TOKEN expose the full Knowledge-Graph read/write API to any LAN-reachable client. An attacker on the same network can read, write, or delete all memory entries — including system://boot and core://* URIs that auto-load into downstream agent sessions, enabling persistent prompt-injection. This vulnerability is fixed in 2.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44830.json
- https://github.com/Dataojitori/nocturne_memory/security/advisories/GHSA-crr4-xrj9-ww8g
- https://nvd.nist.gov/vuln/detail/CVE-2026-44830
