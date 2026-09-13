# [M] Actual Sync Server has an Authenticated Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-27vg-33gh-4hwg
CVE: CVE-2026-3089
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-27vg-33gh-4hwg
Type: github-advisory

## Affected
- npm: `@actual-app/sync-server` — affected >=0 <26.3.0

## Details
# Description

Actual Sync Server allows authenticated users to upload files through `POST /sync/upload-user-file`. In versions prior to 26.3.0, improper validation of the user-controlled `x-actual-file-id` header means that traversal segments (`../`) can escape the intended directory and write files outside `userFiles`.

## Mitigations
The vulnerability can be mitigated in prior versions by running the sync server in a filesystem sandbox.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-27vg-33gh-4hwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-3089
- https://github.com/actualbudget/actual/pull/7067
- https://github.com/actualbudget/actual/commit/18072e1d8b5281db43ded8b21433ee177bae9dfa
- https://fluidattacks.com/advisories/fugue
- https://github.com/actualbudget/actual
