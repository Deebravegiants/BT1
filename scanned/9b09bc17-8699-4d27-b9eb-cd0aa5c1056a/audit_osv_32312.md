# [M] PwnDoc Arbitrary File Write to RCE using Path Traversal in template update from backup templates.json

## Summary
Severity: Medium
Advisory: CVE-2025-27413
Aliases: GHSA-r3vj-47cf-4672
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-02-28
Source: https://osv.dev/vulnerability/CVE-2025-27413
Type: osv

## Details
PwnDoc is a penetration test reporting application. Prior to version 1.2.0, the backup restore functionality allows an administrator to import raw data into the database, including Path Traversal (`../`) sequences. This is problematic for the template update functionality as it uses the path from the database to write arbitrary content to, potentially overwriting source code to achieve Remote Code Execution. Any user with the `backups:create`, `backups:update` and `templates:update` permissions (only administrators by default) can write arbitrary content to anywhere on the filesystem. By overwriting source code, it is possible to achieve Remote Code Execution. Version 1.2.0 fixes the issue.

## References
- https://github.com/pwndoc/pwndoc/blob/14acb704891245bf1703ce6296d62112e85aa995/backend/src/models/template.js#L170-L175
- https://github.com/pwndoc/pwndoc/blob/14acb704891245bf1703ce6296d62112e85aa995/backend/src/routes/backup.js#L826-L827
- https://github.com/pwndoc/pwndoc/blob/14acb704891245bf1703ce6296d62112e85aa995/backend/src/routes/template.js#L63-L66
- https://github.com/pwndoc/pwndoc/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27413.json
- https://github.com/pwndoc/pwndoc/security/advisories/GHSA-r3vj-47cf-4672
- https://nvd.nist.gov/vuln/detail/CVE-2025-27413
- https://github.com/pwndoc/pwndoc/commit/68aa1ea676a91e17bfb333a27571151bd07fb21d
