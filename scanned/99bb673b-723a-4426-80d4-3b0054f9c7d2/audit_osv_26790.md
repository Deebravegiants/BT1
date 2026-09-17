# [H] fs/ntfs3: Fix slab-out-of-bounds read in hdr_delete_de()

## Summary
Severity: High
Advisory: CVE-2023-53988
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-53988
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix slab-out-of-bounds read in hdr_delete_de()

Here is a BUG report from syzbot:

BUG: KASAN: slab-out-of-bounds in hdr_delete_de+0xe0/0x150 fs/ntfs3/index.c:806
Read of size 16842960 at addr ffff888079cc0600 by task syz-executor934/3631

Call Trace:
 memmove+0x25/0x60 mm/kasan/shadow.c:54
 hdr_delete_de+0xe0/0x150 fs/ntfs3/index.c:806
 indx_delete_entry+0x74f/0x3670 fs/ntfs3/index.c:2193
 ni_remove_name+0x27a/0x980 fs/ntfs3/frecord.c:2910
 ntfs_unlink_inode+0x3d4/0x720 fs/ntfs3/inode.c:1712
 ntfs_rename+0x41a/0xcb0 fs/ntfs3/namei.c:276

Before using the meta-data in struct INDEX_HDR, we need to
check index header valid or not. Otherwise, the corruptedi
(or malicious) fs image can cause out-of-bounds access which
could make kernel panic.

## References
- https://git.kernel.org/stable/c/114204d25e1dffdd3a0c1cfbba219afd344f4b4f
- https://git.kernel.org/stable/c/4a034ece7e2877673d9085d6e7ed45e6ee40b761
- https://git.kernel.org/stable/c/9163a5b4ed290da4a7d23fa92533e0e81fd0166e
- https://git.kernel.org/stable/c/ab84eee4c7ab929996602eda7832854c35a6dda2
- https://git.kernel.org/stable/c/c58ea97aa94f033ee64a8cb6587d84a9849b6216
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53988.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
