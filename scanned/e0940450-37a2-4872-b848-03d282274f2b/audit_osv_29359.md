# [H] nilfs2: fix inode number range checks

## Summary
Severity: High
Advisory: CVE-2024-42105
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42105
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix inode number range checks

Patch series "nilfs2: fix potential issues related to reserved inodes".

This series fixes one use-after-free issue reported by syzbot, caused by
nilfs2's internal inode being exposed in the namespace on a corrupted
filesystem, and a couple of flaws that cause problems if the starting
number of non-reserved inodes written in the on-disk super block is
intentionally (or corruptly) changed from its default value.  


This patch (of 3):

In the current implementation of nilfs2, "nilfs->ns_first_ino", which
gives the first non-reserved inode number, is read from the superblock,
but its lower limit is not checked.

As a result, if a number that overlaps with the inode number range of
reserved inodes such as the root directory or metadata files is set in the
super block parameter, the inode number test macros (NILFS_MDT_INODE and
NILFS_VALID_INODE) will not function properly.

In addition, these test macros use left bit-shift calculations using with
the inode number as the shift count via the BIT macro, but the result of a
shift calculation that exceeds the bit width of an integer is undefined in
the C specification, so if "ns_first_ino" is set to a large value other
than the default value NILFS_USER_INO (=11), the macros may potentially
malfunction depending on the environment.

Fix these issues by checking the lower bound of "nilfs->ns_first_ino" and
by preventing bit shifts equal to or greater than the NILFS_USER_INO
constant in the inode number test macros.

Also, change the type of "ns_first_ino" from signed integer to unsigned
integer to avoid the need for type casting in comparisons such as the
lower bound check introduced this time.

## References
- https://git.kernel.org/stable/c/08cab183a624ba71603f3754643ae11cab34dbc4
- https://git.kernel.org/stable/c/1c91058425a01131ea30dda6cf43c67b17884d6a
- https://git.kernel.org/stable/c/3be4dcc8d7bea52ea41f87aa4bbf959efe7a5987
- https://git.kernel.org/stable/c/57235c3c88bb430043728d0d02f44a4efe386476
- https://git.kernel.org/stable/c/731011ac6c37cbe97ece229fc6daa486276052c5
- https://git.kernel.org/stable/c/9194f8ca57527958bee207919458e372d638d783
- https://git.kernel.org/stable/c/e2fec219a36e0993642844be0f345513507031f4
- https://git.kernel.org/stable/c/fae1959d6ab2c52677b113935e36ab4e25df37ea
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42105.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42105
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
