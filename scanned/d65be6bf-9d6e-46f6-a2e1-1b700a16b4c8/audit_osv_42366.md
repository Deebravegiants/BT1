# [C] ArcadeDB before 26.7.2 Authentication Bypass via ALTER TYPE

## Summary
Severity: Critical
Advisory: CVE-2026-67344
Aliases: GHSA-8vr5-263f-x5r3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67344
Type: osv

## Details
ArcadeDB before 26.7.2 fails to enforce the UPDATE_SCHEMA database permission on the ALTER TYPE ... CUSTOM and ALTER TYPE ... BUCKETSELECTIONSTRATEGY SQL operations, which map to setCustomValue and setBucketSelectionStrategy in LocalDocumentType. An authenticated user with only read access (e.g., a read-only API token) can submit these ALTER TYPE statements via the HTTP command endpoint to mutate a type's custom schema metadata and bucket-selection strategy, bypassing the documented updateSchema permission boundary and potentially corrupting schema metadata and record routing.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-8vr5-263f-x5r3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67344.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67344
- https://www.vulncheck.com/advisories/arcadedb-before-authentication-bypass-via-alter-type
