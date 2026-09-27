# [H] Actual: Shared users can perform owner-only file management actions

## Summary
Severity: High
Advisory: CVE-2026-50007
Aliases: GHSA-23vm-ffgg-qvjr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-50007
Type: osv

## Details
Actual is an open-source personal finance application. Prior to 26.7.0, a missing authorization issue allows a shared user with user_access on a budget file to perform owner-only file management actions. A non-owner shared user can call file-management endpoints intended for higher-privilege users, including /delete-user-file, /reset-user-file, and /user-create-key, because requireFileAccess treats ordinary shared access as sufficient for file-management operations that should be restricted to the file owner or an administrator. This issue is fixed in version 26.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50007.json
- https://github.com/actualbudget/actual/security/advisories/GHSA-23vm-ffgg-qvjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-50007
- https://github.com/actualbudget/actual/commit/18a8dc03c48eeb2e8252669a80673e6a9933b5fd
- https://github.com/actualbudget/actual/commit/3b9e79ed5ee795a80bbae214d6ebb2755289d7f2
- https://github.com/actualbudget/actual/pull/7977
- https://github.com/actualbudget/actual/pull/8333
