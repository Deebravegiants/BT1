# [C] OpenClaw < 2026.6.5 Authorization Bypass via Node Exec Approvals

## Summary
Severity: Critical
Advisory: CVE-2026-62228
Aliases: GHSA-8f46-3xx3-8c9m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62228
Type: osv

## Details
OpenClaw before 2026.6.5 contain an authorization bypass vulnerability in node exec approvals that allows lower-trust callers to execute actions beyond their intended authorization by using different gateway and node environments. Attackers can exploit mismatched environment configurations to persist or execute actions that exceed the caller's approved permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62228.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8f46-3xx3-8c9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-62228
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-node-exec-approvals
- https://github.com/openclaw/openclaw
