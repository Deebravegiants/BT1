# [C] daptin - Authentication Bypass via Null Owner Permission Check on usergroup Objects

## Summary
Severity: Critical
Advisory: CVE-2026-72575
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72575
Type: osv

## Details
An improper authorization vulnerability in daptin through v0.12.34 allows unauthenticated remote attackers to read, create, update, and delete usergroup records. The permission check functions (CanRead, CanPeek, CanCreate, CanUpdate, CanDelete, CanRefer) in server/permission/permission.go return true whenever p.UserId equals the requesting userId, but fail to reject the null/zero reference — unlike CanExecute, which explicitly guards it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72575.json
- https://github.com/daptin/daptin
- https://nvd.nist.gov/vuln/detail/CVE-2026-72575
- https://github.com/daptin/daptin/blob/master/server/permission/permission.go
