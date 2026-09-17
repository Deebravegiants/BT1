# [M] Flowsint: Cypher query injection in node type on node creation

## Summary
Severity: Medium
Advisory: CVE-2026-42156
Aliases: GHSA-h5m2-c2c5-968p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42156
Type: osv

## Details
Flowsint is an open-source OSINT graph exploration tool designed for cybersecurity investigation, transparency, and verification. Prior to 1.2.3, a remote attacker can create a node with a malicious type that can escape an existing Cypher query and an adversary can execute an arbitrary Cypher query. This vulnerability is fixed in 1.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42156.json
- https://github.com/reconurge/flowsint/security/advisories/GHSA-h5m2-c2c5-968p
- https://nvd.nist.gov/vuln/detail/CVE-2026-42156
