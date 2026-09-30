# [M] Gokapi has privilege escalation via incomplete API-key permission revocation on user rank demotion

## Summary
Severity: Medium
Advisory: GHSA-q658-hfpg-35qc
CVE: CVE-2026-29061
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-q658-hfpg-35qc
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.3

## Details
### Summary
A privilege escalation vulnerability in the user rank demotion logic allows a demoted user's existing API keys to retain ApiPermManageFileRequests and ApiPermManageLogs permissions, enabling continued access to upload-request management  and log viewing endpoints after the user has been stripped of all privileges.

### Impact
Any user who previously held Admin rank and had API keys with ApiPermManageFileRequests or ApiPermManageLogs retains those capabilities after demotion. This allows offboarded or demoted users to:
  - Create, list, and delete upload requests
  - Read application logs and system status

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-q658-hfpg-35qc
- https://nvd.nist.gov/vuln/detail/CVE-2026-29061
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.3
