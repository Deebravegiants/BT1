# [H] hfsplus: fix uninit-value in copy_name

## Summary
Severity: High
Advisory: CVE-2024-41059
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41059
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <4.19.319, >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfsplus: fix uninit-value in copy_name

[syzbot reported]
BUG: KMSAN: uninit-value in sized_strscpy+0xc4/0x160
 sized_strscpy+0xc4/0x160
 copy_name+0x2af/0x320 fs/hfsplus/xattr.c:411
 hfsplus_listxattr+0x11e9/0x1a50 fs/hfsplus/xattr.c:750
 vfs_listxattr fs/xattr.c:493 [inline]
 listxattr+0x1f3/0x6b0 fs/xattr.c:840
 path_listxattr fs/xattr.c:864 [inline]
 __do_sys_listxattr fs/xattr.c:876 [inline]
 __se_sys_listxattr fs/xattr.c:873 [inline]
 __x64_sys_listxattr+0x16b/0x2f0 fs/xattr.c:873
 x64_sys_call+0x2ba0/0x3b50 arch/x86/include/generated/asm/syscalls_64.h:195
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xcf/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Uninit was created at:
 slab_post_alloc_hook mm/slub.c:3877 [inline]
 slab_alloc_node mm/slub.c:3918 [inline]
 kmalloc_trace+0x57b/0xbe0 mm/slub.c:4065
 kmalloc include/linux/slab.h:628 [inline]
 hfsplus_listxattr+0x4cc/0x1a50 fs/hfsplus/xattr.c:699
 vfs_listxattr fs/xattr.c:493 [inline]
 listxattr+0x1f3/0x6b0 fs/xattr.c:840
 path_listxattr fs/xattr.c:864 [inline]
 __do_sys_listxattr fs/xattr.c:876 [inline]
 __se_sys_listxattr fs/xattr.c:873 [inline]
 __x64_sys_listxattr+0x16b/0x2f0 fs/xattr.c:873
 x64_sys_call+0x2ba0/0x3b50 arch/x86/include/generated/asm/syscalls_64.h:195
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xcf/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
[Fix]
When allocating memory to strbuf, initialize memory to 0.

## References
- https://git.kernel.org/stable/c/0570730c16307a72f8241df12363f76600baf57d
- https://git.kernel.org/stable/c/22999936b91ba545ce1fbbecae6895127945e91c
- https://git.kernel.org/stable/c/34f8efd2743f2d961e92e8e994de4c7a2f9e74a0
- https://git.kernel.org/stable/c/72805debec8f7aa342da194fe0ed7bc8febea335
- https://git.kernel.org/stable/c/ad57dc2caf1e0a3c0a9904400fae7afbc9f74bb2
- https://git.kernel.org/stable/c/c733e24a61cbcff10f660041d6d84d32bb7e4cb4
- https://git.kernel.org/stable/c/d02d8c1dacafb28930c39e16d48e40bb6e4cbc70
- https://git.kernel.org/stable/c/f08956d8e0f80fd0d4ad84ec917302bb2f3a9c6a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41059.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41059
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
