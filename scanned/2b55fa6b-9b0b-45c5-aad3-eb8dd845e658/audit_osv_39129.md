# [H] JunoClaw: SSRF in WAVS computeDataVerify allows cloud-metadata and internal-service access

## Summary
Severity: High
Advisory: CVE-2026-43993
Aliases: GHSA-q545-mvjf-q9pg
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43993
Type: osv

## Details
JunoClaw is an agentic AI platform built on Juno Network. Prior to 0.x.y-security-1, the WAVS bridge's computeDataVerify called fetch() on agent-supplied URLs without validating scheme, port, or resolved IP, resulting in an SSRF vulnerability. This vulnerability is fixed in 0.x.y-security-1.

## References
- https://github.com/Dragonmonk111/junoclaw/releases/tag/v0.x.y-security-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43993.json
- https://github.com/Dragonmonk111/junoclaw/security/advisories/GHSA-q545-mvjf-q9pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-43993
- https://github.com/Dragonmonk111/junoclaw/commit/a168608
