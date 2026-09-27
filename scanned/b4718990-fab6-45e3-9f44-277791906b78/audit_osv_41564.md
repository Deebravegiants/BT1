# [C] OpenClaw < 2026.6.6 Authentication Bypass via Environment Filtering

## Summary
Severity: Critical
Advisory: CVE-2026-62199
Aliases: GHSA-hjr6-g723-hmfm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62199
Type: osv

## Details
OpenClaw versions before 2026.6.6 contain a flaw in host exec environment filtering that can miss interpreter startup variables. When the affected feature is enabled and reachable, a lower-trust caller or configured input path can supply crafted environment variables to execute or persist actions beyond the caller's intended authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62199.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hjr6-g723-hmfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-62199
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-environment-filtering
- https://github.com/openclaw/openclaw
