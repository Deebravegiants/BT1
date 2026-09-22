# [M] OpenClaw 2026.4.12-beta.1 < 2026.6.6 Authorization Bypass via message actions

## Summary
Severity: Medium
Advisory: CVE-2026-62205
Aliases: GHSA-p5xh-frrh-cmgj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62205
Type: osv

## Details
OpenClaw versions 2026.4.12-beta.1 before 2026.6.6 contain a missing-authorization vulnerability in the MS Teams message actions feature. When the affected feature is enabled and reachable, a lower-trust caller or a configured input path can perform actions that should have required a stronger authorization or policy check. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path. The issue is fixed in 2026.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62205.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p5xh-frrh-cmgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-62205
- https://www.vulncheck.com/advisories/openclaw-beta-1-authorization-bypass-via-message-actions
- https://github.com/openclaw/openclaw
