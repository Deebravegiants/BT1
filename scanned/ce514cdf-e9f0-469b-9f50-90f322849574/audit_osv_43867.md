# [M] SWE-agent Trajectory Inspector Path Traversal File Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-75482
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75482
Type: osv

## Details
SWE-agent's trajectory inspector (sweagent inspector), confirmed in v1.1.0, is an HTTP server that joins request paths to the trajectory directory in its /trajectory/ handler without rejecting parent-directory ('..') references, bypassing the built-in path sanitization. The server binds all interfaces (0.0.0.0), applies wildcard CORS, and requires no authentication. An unauthenticated network client (or a malicious web page via CORS) can use path traversal sequences to read files outside the intended directory. Because the read sink parses targets as trajectory JSON, disclosure is constrained to JSON files shaped like a trajectory, which can contain repository contents, command output, and secrets/API keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75482.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75482
- https://www.vulncheck.com/advisories/swe-agent-trajectory-inspector-path-traversal-file-disclosure
- https://github.com/SWE-agent/SWE-agent/issues/1472
- https://github.com/SWE-agent/SWE-agent
- https://github.com/SWE-agent/SWE-agent/blob/main/sweagent/inspector/server.py
