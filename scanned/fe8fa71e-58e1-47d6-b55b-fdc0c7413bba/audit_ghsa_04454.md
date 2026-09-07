# [H] Hermes Agent contains a DNS rebinding vulnerability in WebSocket endpoints that allows remote attackers to bypass Host and Origin validation

## Summary
Severity: High
Advisory: GHSA-4pqm-j46f-795x
CVE: CVE-2026-53869
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-4pqm-j46f-795x
Type: github-advisory

## Affected
- PyPI: `hermes-agent` — affected >=0 <0.16.0

## Details
Hermes Agent before 0.16.0 contains a DNS rebinding vulnerability in WebSocket endpoints that allows remote attackers to bypass Host and Origin validation. FastAPI HTTP middleware does not execute for WebSocket upgrade requests on /api/pty, /api/ws, /api/pub, and /api/events endpoints, enabling attackers to exploit DNS rebinding and inject malicious commands or read terminal output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53869
- https://github.com/NousResearch/hermes-agent/pull/30221
- https://github.com/NousResearch/hermes-agent/pull/31685
- https://github.com/NousResearch/hermes-agent/commit/d9ec90585cf7616b5972e44cf8d92bb569fc3feb
- https://github.com/NousResearch/hermes-agent
- https://github.com/NousResearch/hermes-agent/releases/tag/v2026.6.5
- https://www.vulncheck.com/advisories/hermes-agent-dns-rebinding-bypass-via-websocket-endpoints
