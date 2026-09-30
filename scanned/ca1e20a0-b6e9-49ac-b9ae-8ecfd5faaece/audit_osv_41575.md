# [M] OpenClaw < 2026.5.28 Bot Framework SSRF via serviceUrl Parameter Validation

## Summary
Severity: Medium
Advisory: CVE-2026-62214
Aliases: GHSA-prwc-c6w5-mmgr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62214
Type: osv

## Details
OpenClaw versions before 2026.5.28 Bot Framework contains an improper input validation vulnerability that allows lower-trust callers to expose bot tokens and credentials by failing to properly validate serviceUrl parameters. Attackers can supply malicious serviceUrl values through configured input paths to retrieve sensitive authentication data outside the trusted boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62214.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-prwc-c6w5-mmgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-62214
- https://www.vulncheck.com/advisories/openclaw-bot-framework-ssrf-via-serviceurl-parameter-validation
- https://github.com/openclaw/openclaw
