# [M] PwnDoc Arbitrary File Write to RCE using Path Traversal in backup restore as admin

## Summary
Severity: Medium
Advisory: CVE-2025-27410
Aliases: GHSA-mxw8-vgvx-89hx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-02-28
Source: https://osv.dev/vulnerability/CVE-2025-27410
Type: osv

## Details
PwnDoc is a penetration test reporting application. Prior to version 1.2.0, the backup restore functionality is vulnerable to path traversal in the TAR entry's name, allowing an attacker to overwrite any file on the system with their content. By overwriting an included `.js` file and restarting the container, this allows for Remote Code Execution as an administrator. The remote code execution occurs because any user with the `backups:create` and `backups:update` (only administrators by default) is able to overwrite any file on the system. Version 1.2.0 fixes the issue.

## References
- https://github.com/pwndoc/pwndoc/blob/14acb704891245bf1703ce6296d62112e85aa995/backend/src/routes/backup.js#L527
- https://github.com/pwndoc/pwndoc/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27410.json
- https://github.com/pwndoc/pwndoc/security/advisories/GHSA-mxw8-vgvx-89hx
- https://nvd.nist.gov/vuln/detail/CVE-2025-27410
- https://github.com/pwndoc/pwndoc/commit/98f284291d73d3a0b11d3181d845845c192d1080
