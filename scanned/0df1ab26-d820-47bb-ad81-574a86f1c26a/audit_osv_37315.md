# [H] Session authentication bypass in Coral Server session creation endpoint

## Summary
Severity: High
Advisory: CVE-2026-30970
Aliases: GHSA-wqfm-hhqf-9hgp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30970
Type: osv

## Details
Coral Server is open collaboration infrastructure that enables communication, coordination, trust and payments for The Internet of Agents. Prior to 1.1.0, Coral Server allowed the creation of agent sessions through the /api/v1/sessions endpoint without strong authentication. This endpoint performs resource-intensive initialization operations including container spawning and memory context creation. An attacker capable of accessing the endpoint could create sessions or consume system resources without proper authorization. This vulnerability is fixed in 1.1.0.

## References
- https://github.com/Coral-Protocol/coral-server/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30970.json
- https://github.com/Coral-Protocol/coral-server/security/advisories/GHSA-wqfm-hhqf-9hgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-30970
