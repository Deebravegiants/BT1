# [M] fs/ntfs3: Fix null-ptr-deref on inode->i_op in ntfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53294
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53294
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.112, >=5.16.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix null-ptr-deref on inode->i_op in ntfs_lookup()

Syzbot reported a null-ptr-deref bug:

ntfs3: loop0: Different NTFS' sector size (1024) and media sector size
(512)
ntfs3: loop0: Mark volume as dirty due to NTFS errors
general protection fault, probably for non-canonical address
0xdffffc0000000001: 0000 [#1] PREEMPT SMP KASAN
KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
RIP: 0010:d_flags_for_inode fs/dcache.c:1980 [inline]
RIP: 0010:__d_add+0x5ce/0x800 fs/dcache.c:2796
Call Trace:
 <TASK>
 d_splice_alias+0x122/0x3b0 fs/dcache.c:3191
 lookup_open fs/namei.c:3391 [inline]
 open_last_lookups fs/namei.c:3481 [inline]
 path_openat+0x10e6/0x2df0 fs/namei.c:3688
 do_filp_open+0x264/0x4f0 fs/namei.c:3718
 do_sys_openat2+0x124/0x4e0 fs/open.c:1310
 do_sys_open fs/open.c:1326 [inline]
 __do_sys_open fs/open.c:1334 [inline]
 __se_sys_open fs/open.c:1330 [inline]
 __x64_sys_open+0x221/0x270 fs/open.c:1330
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

If the MFT record of ntfs inode is not a base record, inode->i_op can be
NULL. And a null-ptr-deref may happen:

ntfs_lookup()
    dir_search_u() # inode->i_op is set to NULL
    d_splice_alias()
        __d_add()
            d_flags_for_inode() # inode->i_op->get_link null-ptr-deref

Fix this by adding a Check on inode->i_op before calling the
d_splice_alias() function.

## References
- https://git.kernel.org/stable/c/254e69f284d7270e0abdc023ee53b71401c3ba0c
- https://git.kernel.org/stable/c/2ba22cbc6a1cf4b58195adbee0b80262e53992d3
- https://git.kernel.org/stable/c/d69d5e2a81df94534bdb468bcdd26060fcb7191a
- https://git.kernel.org/stable/c/e78240bc4b94fc42854d65e657bb998100cc8e1b
- https://git.kernel.org/stable/c/f8d9e062a695a3665c4635c4f216a75912687598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53294.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53294
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
