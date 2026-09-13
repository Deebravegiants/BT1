# [H] Coral Server has insufficient agent authentication in session communication channels

## Summary
Severity: High
Advisory: CVE-2026-30969
Aliases: GHSA-ccx7-7wv9-c55x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30969
Type: osv

## Details
Coral Server is open collaboration infrastructure that enables communication, coordination, trust and payments for The Internet of Agents. Prior to 1.1.0, Coral Server did not enforce strong authentication between agents and the server within an active session. This could allow an attacker who obtained or predicted a session identifier to impersonate an agent or join an existing session. This vulnerability is fixed in 1.1.0.

## References
- https://github.com/Coral-Protocol/coral-server/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30969.json
- https://github.com/Coral-Protocol/coral-server/security/advisories/GHSA-ccx7-7wv9-c55x
- https://nvd.nist.gov/vuln/detail/CVE-2026-30969
