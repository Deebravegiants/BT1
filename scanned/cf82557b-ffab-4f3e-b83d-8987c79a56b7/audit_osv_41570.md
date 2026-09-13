# [C] OpenClaw < 2026.6.5 Authentication Bypass via Admin Tools

## Summary
Severity: Critical
Advisory: CVE-2026-62207
Aliases: GHSA-cf2p-f286-mphf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62207
Type: osv

## Details
OpenClaw versions before 2026.6.5 contain an authentication bypass vulnerability that allows lower-trust callers to reach admin-scoped tools. Attackers can perform actions requiring stronger authorization by exploiting insufficient policy checks on configured input paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62207.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cf2p-f286-mphf
- https://nvd.nist.gov/vuln/detail/CVE-2026-62207
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-admin-tools
- https://github.com/openclaw/openclaw
