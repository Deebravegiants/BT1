# [H] rsync < 3.5.0 Symlink Race Condition via ACL/xattr Application

## Summary
Severity: High
Advisory: CVE-2026-53799
Aliases: GHSA-phxh-hjqv-39c9
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53799
Type: osv

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability that allows local attackers to cause rsync to apply arbitrary ACLs or extended attributes to unintended files by substituting a symlink at a predictable destination path between the file write and the subsequent acl_set_file() or lsetxattr() call. Attackers can exploit this timing window to redirect ACL and xattr application through a crafted symlink to files outside the intended destination tree, potentially granting elevated permissions and enabling local privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53799.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-phxh-hjqv-39c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-53799
- https://www.vulncheck.com/advisories/rsync-symlink-race-condition-via-acl-xattr-application
- https://github.com/RsyncProject/rsync
