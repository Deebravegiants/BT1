# [H] ntfs: Fix panic about slab-out-of-bounds caused by ntfs_listxattr()

## Summary
Severity: High
Advisory: CVE-2023-53420
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53420
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: Fix panic about slab-out-of-bounds caused by ntfs_listxattr()

Here is a BUG report from syzbot:

BUG: KASAN: slab-out-of-bounds in ntfs_list_ea fs/ntfs3/xattr.c:191 [inline]
BUG: KASAN: slab-out-of-bounds in ntfs_listxattr+0x401/0x570 fs/ntfs3/xattr.c:710
Read of size 1 at addr ffff888021acaf3d by task syz-executor128/3632

Call Trace:
 ntfs_list_ea fs/ntfs3/xattr.c:191 [inline]
 ntfs_listxattr+0x401/0x570 fs/ntfs3/xattr.c:710
 vfs_listxattr fs/xattr.c:457 [inline]
 listxattr+0x293/0x2d0 fs/xattr.c:804

Fix the logic of ea_all iteration. When the ea->name_len is 0,
return immediately, or Add2Ptr() would visit invalid memory
in the next loop.

[almaz.alexandrovich@paragon-software.com: lines of the patch have changed]

## References
- https://git.kernel.org/stable/c/3c675ddffb17a8b1e32efad5c983254af18b12c2
- https://git.kernel.org/stable/c/721b75ea2dfce53a8890dff92ae01afca8e74f88
- https://git.kernel.org/stable/c/c86a2517df6c9304db8fb12b77136ec7a5d85994
- https://git.kernel.org/stable/c/f3380d895e28a32632eb3609f5bd515adee4e5a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53420.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53420
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
