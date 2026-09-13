# [C] OpenClaw 2026.6.1 < 2026.6.9 Privilege Escalation via Cron

## Summary
Severity: Critical
Advisory: CVE-2026-62202
Aliases: GHSA-mm9g-83wh-mhwj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62202
Type: osv

## Details
OpenClaw versions 2026.6.1 before 2026.6.9 contain a privilege escalation vulnerability in isolated cron jobs that allows lower-trust callers to regain denied execution tools. Attackers can execute or persist actions beyond their intended authorization by leveraging misconfigured input paths in the affected cron feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62202.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mm9g-83wh-mhwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-62202
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-cron
- https://github.com/openclaw/openclaw
