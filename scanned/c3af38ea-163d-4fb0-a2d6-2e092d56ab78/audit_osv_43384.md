# [H] filebrowser before 2.63.19 Out-of-Scope File Deletion via Symlink

## Summary
Severity: High
Advisory: CVE-2026-73613
Aliases: GHSA-m9f5-2232-frp6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73613
Type: osv

## Details
filebrowser versions before 2.63.19 contain an out-of-scope file deletion vulnerability in the TUS upload cache eviction mechanism that allows authenticated users with only Create permission to delete arbitrary files outside their scope. Attackers can swap an ancestor directory with a symlink during the cache TTL window to redirect the raw os.Remove call to an out-of-scope target, bypassing ScopedFs scope guards and Perm.Delete checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73613.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-m9f5-2232-frp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-73613
- https://www.vulncheck.com/advisories/filebrowser-before-out-of-scope-file-deletion-via-symlink
