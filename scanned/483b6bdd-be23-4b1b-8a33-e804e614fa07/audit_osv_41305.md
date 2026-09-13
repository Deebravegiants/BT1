# [H] OpenClaw < 2026.5.28 - Credential Override via Workspace Dotenv Files

## Summary
Severity: High
Advisory: CVE-2026-59261
Aliases: GHSA-4pqj-3c56-5fqq
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59261
Type: osv

## Details
OpenClaw before 2026.5.28 contains a credential exposure vulnerability where workspace dotenv files can override provider credentials. Attackers with lower-trust access to configured input paths can expose sensitive data and credentials that should remain within trusted boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59261.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4pqj-3c56-5fqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-59261
- https://www.vulncheck.com/advisories/openclaw-credential-override-via-workspace-dotenv-files
