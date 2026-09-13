# [M] stoatchat before 0.15.0 Permission Bypass via message_fetch

## Summary
Severity: Medium
Advisory: CVE-2026-73059
Aliases: GHSA-8qp4-h9xf-2vqr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2026-73059
Type: osv

## Details
stoatchat before 0.15.0 contains a permission bypass vulnerability in the message_fetch route that checks only ViewChannel permission instead of requiring ReadMessageHistory. Attackers with ViewChannel access but ReadMessageHistory denied can retrieve individual message content by ID, bypassing the intended history restriction enforced by bulk read routes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73059.json
- https://github.com/stoatchat/stoatchat/security/advisories/GHSA-8qp4-h9xf-2vqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-73059
- https://www.vulncheck.com/advisories/stoatchat-before-permission-bypass-via-message-fetch
