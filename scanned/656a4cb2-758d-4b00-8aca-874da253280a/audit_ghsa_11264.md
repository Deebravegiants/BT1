# [M] Gokapi vulnerable to Privilege Escalation in File Replace

## Summary
Severity: Medium
Advisory: GHSA-j6jp-78w8-34x6
CVE: CVE-2026-30943
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-j6jp-78w8-34x6
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.4

## Details
## Summary

An insufficient authorization check in the file replace API allows a user with only list visibility permission (`UserPermListOtherUploads`) to delete another user's file by abusing the `deleteNewFile` flag, bypassing the requirement for `UserPermDeleteOtherUploads`.

### Impact

Any authenticated user with `PERM_REPLACE` (replace own files) and `PERM_LIST` (view other users' uploads) can delete any other user's file without needing `PERM_DELETE`.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-j6jp-78w8-34x6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30943
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.4
- https://pkg.go.dev/vuln/GO-2026-4696
