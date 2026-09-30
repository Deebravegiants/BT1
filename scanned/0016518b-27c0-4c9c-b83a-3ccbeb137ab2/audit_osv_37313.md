# [H] Coral Server has insufficient validation of agent identity for SSE connections

## Summary
Severity: High
Advisory: CVE-2026-30968
Aliases: GHSA-2rj5-3pgm-xqw9
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30968
Type: osv

## Details
Coral Server is open collaboration infrastructure that enables communication, coordination, trust and payments for The Internet of Agents. Prior to 1.1.0, the SSE endpoint (/sse/v1/...) in Coral Server did not strongly validate that a connecting agent was a legitimate participant in the session. This could theoretically allow unauthorized message injection or observation. This vulnerability is fixed in 1.1.0.

## References
- https://github.com/Coral-Protocol/coral-server/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30968.json
- https://github.com/Coral-Protocol/coral-server/security/advisories/GHSA-2rj5-3pgm-xqw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-30968
