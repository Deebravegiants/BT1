# [C] selinux,smack: don't bypass permissions check in inode_setsecctx hook

## Summary
Severity: Critical
Advisory: CVE-2024-46695
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46695
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.49, >=6.7.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

selinux,smack: don't bypass permissions check in inode_setsecctx hook

Marek Gresko reports that the root user on an NFS client is able to
change the security labels on files on an NFS filesystem that is
exported with root squashing enabled.

The end of the kerneldoc comment for __vfs_setxattr_noperm() states:

 *  This function requires the caller to lock the inode's i_mutex before it
 *  is executed. It also assumes that the caller will make the appropriate
 *  permission checks.

nfsd_setattr() does do permissions checking via fh_verify() and
nfsd_permission(), but those don't do all the same permissions checks
that are done by security_inode_setxattr() and its related LSM hooks do.

Since nfsd_setattr() is the only consumer of security_inode_setsecctx(),
simplest solution appears to be to replace the call to
__vfs_setxattr_noperm() with a call to __vfs_setxattr_locked().  This
fixes the above issue and has the added benefit of causing nfsd to
recall conflicting delegations on a file when a client tries to change
its security label.

## References
- https://git.kernel.org/stable/c/2dbc4b7bac60b02cc6e70d05bf6a7dfd551f9dda
- https://git.kernel.org/stable/c/459584258d47ec3cc6245a82e8a49c9d08eb8b57
- https://git.kernel.org/stable/c/76a0e79bc84f466999fa501fce5bf7a07641b8a7
- https://git.kernel.org/stable/c/eebec98791d0137e455cc006411bb92a54250924
- https://git.kernel.org/stable/c/f71ec019257ba4f7ab198bd948c5902a207bad96
- https://git.kernel.org/stable/c/fe0cd53791119f6287b6532af8ce41576d664930
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46695.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
