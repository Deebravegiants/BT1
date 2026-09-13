# [H] Rsync < 3.4.3 Symlink Race Condition via Path-Based Syscalls

## Summary
Severity: High
Advisory: CVE-2026-43619
Aliases: GHSA-4h9m-w5ff-j735
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-43619
Type: osv

## Details
Rsync version 3.4.2 and prior contain symlink race condition vulnerabilities in path-based system calls including chmod, lchown, utimes, rename, unlink, mkdir, symlink, mknod, link, rmdir, and lstat that allow local attackers to redirect operations to files outside the exported rsync module. Attackers with local filesystem access can exploit the timing window between path resolution and syscall execution by swapping symlinks to apply sender-supplied permissions, ownership, timestamps, or filenames to arbitrary files outside the intended module boundary on rsync daemons configured with 'use chroot = no'.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43619.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-4h9m-w5ff-j735
- https://nvd.nist.gov/vuln/detail/CVE-2026-43619
- https://www.vulncheck.com/advisories/rsync-symlink-race-condition-via-path-based-syscalls
- https://github.com/RsyncProject/rsync
