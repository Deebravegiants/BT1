# [H] VoltAgent Memory API Handlers Missing Ownership Checks

## Summary
Severity: High
Advisory: CVE-2026-82283
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82283
Type: osv

## Details
VoltAgent through 2.1.20 fails to validate conversation ownership in memory API handlers, allowing authenticated users to access other users' conversations. Attackers can read, modify, and delete arbitrary conversations and messages by supplying caller-controlled identifiers to memory endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82283.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82283
- https://www.vulncheck.com/advisories/voltagent-memory-api-handlers-missing-ownership-checks
- https://github.com/VoltAgent/voltagent/issues/1371
- https://github.com/VoltAgent/voltagent
- https://github.com/VoltAgent/voltagent/blob/44b4c8e4998ce56095b2f0e4eaf1a988f5e6d0de/packages/server-core/src/handlers/memory.handlers.ts
