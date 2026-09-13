# [C] OpenClaw < 2026.6.9 Authorization Bypass via flock wrapper

## Summary
Severity: Critical
Advisory: CVE-2026-62190
Aliases: GHSA-3fp5-v549-9v66
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62190
Type: osv

## Details
OpenClaw versions before 2026.6.9 contain an authorization bypass vulnerability in the flock wrapper that allows lower-trust callers to execute or persist actions beyond their intended authorization. Attackers can leverage configured input paths to bypass durable exec approval binding and perform unauthorized operations when the affected feature is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62190.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3fp5-v549-9v66
- https://nvd.nist.gov/vuln/detail/CVE-2026-62190
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-flock-wrapper
- https://github.com/openclaw/openclaw
