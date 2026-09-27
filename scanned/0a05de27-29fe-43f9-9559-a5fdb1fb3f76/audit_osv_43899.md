# [M] ArcadeDB before 26.8.1 Unauthorized Function Deletion via DELETE FUNCTION

## Summary
Severity: Medium
Advisory: CVE-2026-75846
Aliases: GHSA-vv82-qvpf-rjwv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75846
Type: osv

## Details
ArcadeDB before 26.8.1 (affected versions <= 26.7.3) contains a missing authorization vulnerability in the DELETE FUNCTION SQL statement. DeleteFunctionStatement.executeSimple unregisters and persists deletion of a server-side function without any checkPermissionsOnDatabase (UPDATE_SCHEMA) check. Any user with database access can execute DELETE FUNCTION via the command API (POST /api/v1/command/{db}) to permanently remove any registered server-side function, including security-relevant logic, impacting integrity and availability.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-vv82-qvpf-rjwv
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75846.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75846
- https://www.vulncheck.com/advisories/arcadedb-before-unauthorized-function-deletion-via-delete-function
