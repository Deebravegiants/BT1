# [H] CVE-2021-4037

## Summary
Severity: High
Advisory: CVE-2021-4037
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4037
Type: osv

## Details
A vulnerability was found in the fs/inode.c:inode_init_owner() function logic of the LInux kernel that allows local users to create files for the XFS file-system with an unintended group ownership and with group execution and SGID permission bits set, in a scenario where a directory is SGID and belongs to a certain group and is writable by a user who is not a member of this group. This can lead to excessive permissions granted in case when they should not. This vulnerability is similar to the previous CVE-2018-13405 and adds the missed fix for the XFS.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://www.debian.org/security/2022/dsa-5257
- https://access.redhat.com/security/cve/CVE-2021-4037
- https://bugzilla.redhat.com/show_bug.cgi?id=2004810
- https://bugzilla.redhat.com/show_bug.cgi?id=2027239
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=01ea173e103e
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=0fa3ecd87848
