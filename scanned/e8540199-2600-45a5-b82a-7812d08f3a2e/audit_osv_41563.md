# [H] OpenClaw 2026.3.22 < 2026.6.6 Authorization Bypass via WhatsApp Group IDs

## Summary
Severity: High
Advisory: CVE-2026-62196
Aliases: GHSA-fh38-965w-f6c3
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62196
Type: osv

## Details
OpenClaw versions 2026.3.22 before 2026.6.6 contain an authorization bypass vulnerability where WhatsApp group IDs can satisfy elevated sender allowlists. Attackers with lower-trust access can perform actions requiring stronger authorization by leveraging group ID validation in the affected feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62196.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fh38-965w-f6c3
- https://nvd.nist.gov/vuln/detail/CVE-2026-62196
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-whatsapp-group-ids
- https://github.com/openclaw/openclaw
