# [C] OpenClaw < 2026.6.6 Environment Variable Injection via rustup

## Summary
Severity: Critical
Advisory: CVE-2026-62203
Aliases: GHSA-wxh3-g47h-q3mc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62203
Type: osv

## Details
OpenClaw versions before 2026.6.6 contain an environment variable filtering vulnerability in host exec that fails to properly sanitize rustup startup variables. Attackers with lower-trust caller access or configured input paths can execute or persist actions beyond their intended authorization level.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62203.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wxh3-g47h-q3mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-62203
- https://www.vulncheck.com/advisories/openclaw-environment-variable-injection-via-rustup
- https://github.com/openclaw/openclaw
