# [C] OpenClaw < 2026.5.18 Authorization Bypass via Glob Matching

## Summary
Severity: Critical
Advisory: CVE-2026-62229
Aliases: GHSA-34mr-7r3m-gfg7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62229
Type: osv

## Details
OpenClaw before 2026.5.18 contain an authorization bypass vulnerability in exec allowlist glob matching that allows lower-trust callers to execute actions beyond intended authorization. Attackers can craft input paths that traverse the allowlist glob patterns to execute or persist unauthorized actions when the affected feature is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62229.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-34mr-7r3m-gfg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-62229
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-glob-matching
- https://github.com/openclaw/openclaw
