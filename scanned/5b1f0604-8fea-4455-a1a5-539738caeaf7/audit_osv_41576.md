# [C] OpenClaw 2026.5.14-beta.1 < 2026.5.27 Authentication Bypass via exec approvals

## Summary
Severity: Critical
Advisory: CVE-2026-62217
Aliases: GHSA-7jx6-764p-fgg9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62217
Type: osv

## Details
OpenClaw 2026.5.14-beta.1 before 2026.5.27 contain an authorization flaw in the QQBot exec approvals feature. When the feature is enabled and reachable, a lower-trust caller or configured input path could execute or persist actions beyond the caller's intended authorization, allowing non-allowlisted senders to perform unauthorized operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62217.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7jx6-764p-fgg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-62217
- https://www.vulncheck.com/advisories/openclaw-beta-1-authentication-bypass-via-exec-approvals
- https://github.com/openclaw/openclaw
