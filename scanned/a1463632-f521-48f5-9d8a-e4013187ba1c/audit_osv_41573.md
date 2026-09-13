# [M] OpenClaw < 2026.6.1 Credential Redaction Bypass via Trajectory Export

## Summary
Severity: Medium
Advisory: CVE-2026-62211
Aliases: GHSA-j4cx-jvq7-79vm
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62211
Type: osv

## Details
OpenClaw versions before 2026.6.1 contain a credential redaction bypass vulnerability in the trajectory export feature that allows lower-trust callers to access data that should remain within trusted boundaries. Attackers can exploit misconfigured input paths or feature accessibility to expose sensitive credentials and data through the export mechanism.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62211.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j4cx-jvq7-79vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-62211
- https://www.vulncheck.com/advisories/openclaw-credential-redaction-bypass-via-trajectory-export
- https://github.com/openclaw/openclaw
