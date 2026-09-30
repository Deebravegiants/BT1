# [H] OpenClaw 2026.6.6 < 2026.6.9 Authorization Bypass

## Summary
Severity: High
Advisory: CVE-2026-62192
Aliases: GHSA-3pmr-x9g8-m55r
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62192
Type: osv

## Details
OpenClaw versions 2026.6.6 before 2026.6.9 contain an authorization bypass vulnerability in Discord guild actions that allows lower-trust callers to perform actions requiring stronger authorization checks. Attackers can exploit misconfigured input paths to skip cross-provider requester authorization and execute restricted operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62192.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3pmr-x9g8-m55r
- https://nvd.nist.gov/vuln/detail/CVE-2026-62192
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass
- https://github.com/openclaw/openclaw
