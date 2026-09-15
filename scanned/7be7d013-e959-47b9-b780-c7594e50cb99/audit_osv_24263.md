# [H] hfs: Fix OOB Write in hfs_asc2mac

## Summary
Severity: High
Advisory: CVE-2022-50747
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50747
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.14 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfs: Fix OOB Write in hfs_asc2mac

Syzbot reported a OOB Write bug:

loop0: detected capacity change from 0 to 64
==================================================================
BUG: KASAN: slab-out-of-bounds in hfs_asc2mac+0x467/0x9a0
fs/hfs/trans.c:133
Write of size 1 at addr ffff88801848314e by task syz-executor391/3632

Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x1b1/0x28e lib/dump_stack.c:106
 print_address_description+0x74/0x340 mm/kasan/report.c:284
 print_report+0x107/0x1f0 mm/kasan/report.c:395
 kasan_report+0xcd/0x100 mm/kasan/report.c:495
 hfs_asc2mac+0x467/0x9a0 fs/hfs/trans.c:133
 hfs_cat_build_key+0x92/0x170 fs/hfs/catalog.c:28
 hfs_lookup+0x1ab/0x2c0 fs/hfs/dir.c:31
 lookup_open fs/namei.c:3391 [inline]
 open_last_lookups fs/namei.c:3481 [inline]
 path_openat+0x10e6/0x2df0 fs/namei.c:3710
 do_filp_open+0x264/0x4f0 fs/namei.c:3740

If in->len is much larger than HFS_NAMELEN(31) which is the maximum
length of an HFS filename, a OOB write could occur in hfs_asc2mac(). In
that case, when the dst reaches the boundary, the srclen is still
greater than 0, which causes a OOB write.
Fix this by adding a check on dstlen in while() before writing to dst
address.

## References
- https://git.kernel.org/stable/c/6a95b17e4d4cd2d8278559f930b447f8c9c8cff9
- https://git.kernel.org/stable/c/7af9cb8cbb81308ce4b06cc7164267faccbf75dd
- https://git.kernel.org/stable/c/8399318b13dc9e0569dee07ba2994098926d4fb2
- https://git.kernel.org/stable/c/88579c158e026860c61c4192531e8bc42f4bc642
- https://git.kernel.org/stable/c/95040de81c629cd8d3c6ab5b50a8bd5088068303
- https://git.kernel.org/stable/c/ae21b03f904736eb2aa9bd119d2a14e741f1681f
- https://git.kernel.org/stable/c/ba8f0ca386dd15acf5a93cbac932392c7818eab4
- https://git.kernel.org/stable/c/c53ed55cb275344086e32a7080a6b19cb183650b
- https://git.kernel.org/stable/c/cff9fefdfbf5744afbb6d70bff2b49ec2065d23d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50747.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
