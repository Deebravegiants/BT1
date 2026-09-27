# [H] ovl: fix UAF in ovl_dentry_update_reval by moving dput() in ovl_link_up

## Summary
Severity: High
Advisory: CVE-2025-21887
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21887
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.247, >=5.11.0 <5.15.179, >=5.16.0 <6.1.130, >=6.2.0 <6.6.81, >=6.5.0 <6.12.18, >=6.7.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovl: fix UAF in ovl_dentry_update_reval by moving dput() in ovl_link_up

The issue was caused by dput(upper) being called before
ovl_dentry_update_reval(), while upper->d_flags was still
accessed in ovl_dentry_remote().

Move dput(upper) after its last use to prevent use-after-free.

BUG: KASAN: slab-use-after-free in ovl_dentry_remote fs/overlayfs/util.c:162 [inline]
BUG: KASAN: slab-use-after-free in ovl_dentry_update_reval+0xd2/0xf0 fs/overlayfs/util.c:167

Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:114
 print_address_description mm/kasan/report.c:377 [inline]
 print_report+0xc3/0x620 mm/kasan/report.c:488
 kasan_report+0xd9/0x110 mm/kasan/report.c:601
 ovl_dentry_remote fs/overlayfs/util.c:162 [inline]
 ovl_dentry_update_reval+0xd2/0xf0 fs/overlayfs/util.c:167
 ovl_link_up fs/overlayfs/copy_up.c:610 [inline]
 ovl_copy_up_one+0x2105/0x3490 fs/overlayfs/copy_up.c:1170
 ovl_copy_up_flags+0x18d/0x200 fs/overlayfs/copy_up.c:1223
 ovl_rename+0x39e/0x18c0 fs/overlayfs/dir.c:1136
 vfs_rename+0xf84/0x20a0 fs/namei.c:4893
...
 </TASK>

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/3594aad97e7be2557ca9fa9c931b206b604028c8
- https://git.kernel.org/stable/c/4b49d939b5a79117f939b77cc67efae2694d9799
- https://git.kernel.org/stable/c/60b4b5c1277fc491da9e1e7abab307bfa39c2db7
- https://git.kernel.org/stable/c/64455c8051c3aedc71abb7ec8d47c80301f99f00
- https://git.kernel.org/stable/c/a7c41830ffcd17b2177a95a9b99b270302090c35
- https://git.kernel.org/stable/c/c84e125fff2615b4d9c259e762596134eddd2f27
- https://git.kernel.org/stable/c/f77618291836168eca99e89cd175256f928f5e64
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21887.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
