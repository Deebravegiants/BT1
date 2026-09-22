# [C] ArcadeDB before 26.8.1 Privilege Escalation via gRPC Transaction

## Summary
Severity: Critical
Advisory: CVE-2026-75843
Aliases: GHSA-p29f-345w-4qwf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75843
Type: osv

## Details
ArcadeDB before 26.8.1 fails to bind the authenticated principal on the gRPC transaction executor thread in beginTransaction, allowing authenticated readers to execute JavaScript commands without scripting authorization checks. Attackers can execute executeCommand with a transaction ID to run unrestricted JavaScript that creates server-wide administrator accounts.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-p29f-345w-4qwf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75843.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75843
- https://www.vulncheck.com/advisories/arcadedb-before-privilege-escalation-via-grpc-transaction
