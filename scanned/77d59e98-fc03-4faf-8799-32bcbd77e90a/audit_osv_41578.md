# [M] OpenClaw 2026.2.12 < 2026.5.26 Authorization Bypass via Blank Agent IDs

## Summary
Severity: Medium
Advisory: CVE-2026-62219
Aliases: GHSA-724r-v4wf-mqc5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62219
Type: osv

## Details
OpenClaw 2026.2.12 before 2026.5.26 contain an authorization bypass vulnerability in the hooks allowedAgentIds validation. A lower-trust caller or configured input path can bypass agent ID restrictions by submitting blank agent IDs, allowing actions that should require stronger authorization or policy checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62219.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-724r-v4wf-mqc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-62219
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-blank-agent-ids
- https://github.com/openclaw/openclaw
