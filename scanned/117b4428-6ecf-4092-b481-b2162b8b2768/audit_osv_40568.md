# [M] Kestra: Cross-Execution File Read via Preview Endpoint (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2026-53577
Aliases: GHSA-r6v3-xxwj-9h42
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53577
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 1.0.45 and 1.3.21, the previewFileFromExecution endpoint (GET /api/v1/{tenant}/executions/{executionId}/file/preview) contains an access control bypass that allows any authenticated user to read output files from any other execution within the same tenant, bypassing execution-level and namespace-level isolation. This vulnerability is fixed in 1.0.45 and 1.3.21.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53577.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-r6v3-xxwj-9h42
- https://nvd.nist.gov/vuln/detail/CVE-2026-53577
