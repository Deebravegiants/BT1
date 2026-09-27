# [M] OpenClaw < 2026.6.8 Authorization Bypass via HTTP Model Override

## Summary
Severity: Medium
Advisory: CVE-2026-62186
Aliases: GHSA-jhfx-v2j8-x3m6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62186
Type: osv

## Details
OpenClaw versions before 2026.6.8 contain an authorization bypass vulnerability in OpenAI-compatible HTTP model overrides that allows lower-trust callers to perform actions requiring stronger authorization checks. Attackers can exploit misconfigured input paths to bypass admin authorization policies and execute restricted operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62186.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jhfx-v2j8-x3m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-62186
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-http-model-override
- https://github.com/openclaw/openclaw
