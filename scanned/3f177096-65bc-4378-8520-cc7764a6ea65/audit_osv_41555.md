# [H] OpenClaw < 2026.6.9 Feishu tools Authorization Bypass

## Summary
Severity: High
Advisory: CVE-2026-62187
Aliases: GHSA-2q7j-2vhx-56g8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62187
Type: osv

## Details
OpenClaw Feishu tools (npm package @openclaw/feishu) in versions <= 2026.6.6 could ignore per-account disablement. A lower-trust caller or a configured input path could perform actions that should have required a stronger authorization or policy check, resulting in unauthorized operations. The issue is fixed in version 2026.6.9. Impact depends on the operator's configuration and whether lower-trust input can reach the affected feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62187.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2q7j-2vhx-56g8
- https://nvd.nist.gov/vuln/detail/CVE-2026-62187
- https://www.vulncheck.com/advisories/openclaw-feishu-tools-authorization-bypass
- https://github.com/openclaw/openclaw
