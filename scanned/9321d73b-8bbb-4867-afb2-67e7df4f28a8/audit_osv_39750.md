# [C] SSHFS Symlink Escape: Rogue SFTP Server → Local File Read/Write

## Summary
Severity: Critical
Advisory: CVE-2026-47187
Aliases: GHSA-pjv6-2c3f-r357
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-47187
Type: osv

## Details
SSHFS is a network filesystem client for connecting to SSH servers. Prior to version 3.7.6, a rogue SFTP server can return absolute symlink targets or relative targets containing parent-directory components that SSHFS passes through FUSE for resolution by the client kernel against the local filesystem. The documented transform_symlinks mitigation does not contain relative targets because transform_symlink() returns early at sshfs.c:2181, while sshfs_readlink() at sshfs.c:2234 to sshfs.c:2236 otherwise copies the server-supplied link target to the kernel. A victim or victim-side tool that follows such a link through ordinary operations such as cp, rsync, backup tooling, or an editor can disclose readable local files back to the server or write server-controlled content to writable local files, potentially including startup or scheduled-task files. This issue is fixed in version 3.7.6.

## References
- https://github.com/libfuse/sshfs/releases/tag/sshfs-3.7.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47187.json
- https://github.com/libfuse/sshfs/security/advisories/GHSA-pjv6-2c3f-r357
- https://nvd.nist.gov/vuln/detail/CVE-2026-47187
- https://github.com/libfuse/sshfs/commit/bcd132f17ccf1b8592a229df797c9b08883fec26
- https://github.com/libfuse/sshfs/pull/361
