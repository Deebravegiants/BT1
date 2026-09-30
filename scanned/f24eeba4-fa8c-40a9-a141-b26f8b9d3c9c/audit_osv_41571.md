# [H] OpenClaw 2026.5.10-beta.1 < 2026.6.5 Authorization Bypass via agent-mode dispatch

## Summary
Severity: High
Advisory: CVE-2026-62209
Aliases: GHSA-wp73-f3gg-w4vr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62209
Type: osv

## Details
OpenClaw versions 2026.5.10-beta.1 before 2026.6.5 contain an authorization bypass in the ClickClack agent-mode dispatch feature, which could ignore the toolsAllow policy check. When the affected feature is enabled and reachable, a lower-trust caller or configured input path could perform actions that should have required a stronger authorization or policy check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62209.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wp73-f3gg-w4vr
- https://nvd.nist.gov/vuln/detail/CVE-2026-62209
- https://www.vulncheck.com/advisories/openclaw-beta-1-authorization-bypass-via-agent-mode-dispatch
- https://github.com/openclaw/openclaw
