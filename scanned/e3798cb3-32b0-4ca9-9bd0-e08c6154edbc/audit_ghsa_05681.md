# [H] SiYuan File Read API Case Sensitivity Bypass can Lead to Path Traversal

## Summary
Severity: High
Advisory: GHSA-f72r-2h5j-7639
CVE: CVE-2026-25992
CWE: CWE-178, CWE-22, CWE-426
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-f72r-2h5j-7639
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
# File Read Interface Case Bypass Vulnerability
## Vulnerability Name
File Read Interface Case Bypass Vulnerability

## Overview
The `/api/file/getFile` endpoint uses **case-sensitive string equality checks** to block access to sensitive files.
On case-insensitive file systems such as **Windows**, attackers can bypass restrictions using mixed-case paths
and read protected configuration files.

## Impact
- Read sensitive information in configuration files (e.g., access codes, API Tokens, sync configurations, etc.).
- Remotely exploitable directly when the service is published without authentication.

## Trigger Conditions
- Running on a **case-insensitive file system**.
- The caller can access `/api/file/getFile` (via CheckAuth or Token injection in published services).

## PoC (Generic Example)
After enabling publication:

**Request:**
```http
POST /api/file/getFile
Content-Type: application/json

{"path":"cOnf/conf.json"}
```

**Expected Result:**
- Successfully return the content of the configuration file.

## Root Cause
Path comparison uses strict case-sensitive string matching, without case normalization or identical file validation.

## Fix Recommendations
- Normalize path casing before comparison (Windows/macOS).
- Use file-level comparison methods such as `os.SameFile`.
- Apply blacklist validation on sensitive paths **after case normalization**.

## Notes
- Environment identifiers and sensitive information have been removed.

## Solution Commit
`399a38893e8719968ea2511e177bb53e09973fa6`

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-f72r-2h5j-7639
- https://nvd.nist.gov/vuln/detail/CVE-2026-25992
- https://github.com/siyuan-note/siyuan/commit/1f02650b3892d2ea3896242dd2422c30bda55e11
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.5.5
