# [M] OpenClaw < 2026.6.9 Authentication Bypass via Moderation Actions

## Summary
Severity: Medium
Advisory: CVE-2026-62206
Aliases: GHSA-f6p7-6326-vf7v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62206
Type: osv

## Details
OpenClaw versions before 2026.6.9 contain a missing authorization vulnerability in Discord moderation actions. In affected versions, a lower-trust caller or configured input path could perform moderation actions that should have required a stronger authorization or policy check. Practical impact depends on the operator's configuration and whether lower-trust input can reach the affected path.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62206.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f6p7-6326-vf7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-62206
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-moderation-actions
- https://github.com/openclaw/openclaw
