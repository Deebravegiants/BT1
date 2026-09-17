# [C] OpenClaw < 2026.6.6 Authentication Bypass via Git ext transport

## Summary
Severity: Critical
Advisory: CVE-2026-62200
Aliases: GHSA-9969-8g9h-rxwm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62200
Type: osv

## Details
OpenClaw versions before 2026.6.6 contain a flaw in host exec environment filtering that could allow Git ext transport to be abused. When the affected feature is enabled and reachable, a lower-trust caller or configured input path could execute or persist actions beyond the caller's intended authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62200.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9969-8g9h-rxwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-62200
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-git-ext-transport
- https://github.com/openclaw/openclaw
