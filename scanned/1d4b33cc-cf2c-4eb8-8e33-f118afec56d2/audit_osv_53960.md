# [M] CVE-2023-34256

## Summary
Severity: Medium
Advisory: CVE-2023-34256
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-31
Source: https://osv.dev/vulnerability/CVE-2023-34256
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.3. There is an out-of-bounds read in crc16 in lib/crc16.c when called from fs/ext4/super.c because ext4_group_desc_csum does not properly check an offset. NOTE: this is disputed by third parties because the kernel is not intended to defend against attackers with the stated "When modifying the block device while it is mounted by the filesystem" access.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://syzkaller.appspot.com/bug?extid=8785e41224a3afd04321
- https://bugzilla.suse.com/show_bug.cgi?id=1211895
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4f04351888a83e595571de672e0a4a8b74f4fb31
