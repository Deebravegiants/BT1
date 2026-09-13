# [H] OpenClaw 2026.1.5 < 2026.2.12 - Missing Authentication in Browser Control HTTP Endpoints

## Summary
Severity: High
Advisory: CVE-2026-28485
Aliases: GHSA-qpjj-47vm-64pj
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-28485
Type: osv

## Details
OpenClaw versions 2026.1.5 prior to 2026.2.12 fail to enforce mandatory authentication on the /agent/act browser-control HTTP route, allowing unauthorized local callers to invoke privileged operations. Remote attackers on the local network or local processes can execute arbitrary browser-context actions and access sensitive in-session data by sending requests to unauthenticated endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28485.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qpjj-47vm-64pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-28485
- https://www.vulncheck.com/advisories/openclaw-missing-authentication-in-browser-control-http-endpoints
- https://github.com/openclaw/openclaw/commit/9230a2ae14307740a13ada7afd6dcfab34e0287f
