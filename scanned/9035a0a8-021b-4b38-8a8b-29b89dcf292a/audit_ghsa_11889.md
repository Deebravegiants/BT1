# [M] Gokapi has Data Leak in Upload Status Stream

## Summary
Severity: Medium
Advisory: GHSA-c36c-7pc2-f2ph
CVE: CVE-2026-28682
CWE: CWE-200, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-c36c-7pc2-f2ph
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.3

## Details
## Description

The upload status SSE implementation on `/uploadStatus` publishes global upload state to any authenticated listener and includes `file_id` values that are not scoped to the requesting user. 

## Impact

Any authenticated user can observe other users' file identifiers and retrieve unauthorized content, causing cross-tenant data exposure and loss of confidentiality for uploaded documents.

*Issue found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-c36c-7pc2-f2ph
- https://nvd.nist.gov/vuln/detail/CVE-2026-28682
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.3
