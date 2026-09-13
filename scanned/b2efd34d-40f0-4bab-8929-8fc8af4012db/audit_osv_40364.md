# [H] ocfs2: fix listxattr handling when the buffer is full

## Summary
Severity: High
Advisory: CVE-2026-53041
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53041
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: fix listxattr handling when the buffer is full

[BUG]
If an OCFS2 inode has both inline and block-based xattrs, listxattr()
can return a size larger than the caller's buffer when the inline names
consume that buffer exactly.

kernel BUG at mm/usercopy.c:102!
Oops: invalid opcode: 0000 [#1] SMP KASAN NOPTI
RIP: 0010:usercopy_abort+0xb7/0xd0 mm/usercopy.c:102
Call Trace:
 __check_heap_object+0xe3/0x120 mm/slub.c:8243
 check_heap_object mm/usercopy.c:196 [inline]
 __check_object_size mm/usercopy.c:250 [inline]
 __check_object_size+0x5c5/0x780 mm/usercopy.c:215
 check_object_size include/linux/ucopysize.h:22 [inline]
 check_copy_size include/linux/ucopysize.h:59 [inline]
 copy_to_user include/linux/uaccess.h:219 [inline]
 listxattr+0xb0/0x170 fs/xattr.c:926
 filename_listxattr fs/xattr.c:958 [inline]
 path_listxattrat+0x137/0x320 fs/xattr.c:988
 __do_sys_listxattr fs/xattr.c:1001 [inline]
 __se_sys_listxattr fs/xattr.c:998 [inline]
 __x64_sys_listxattr+0x7f/0xd0 fs/xattr.c:998
 ...

[CAUSE]
Commit 936b8834366e ("ocfs2: Refactor xattr list and remove
ocfs2_xattr_handler().") replaced the old per-handler list accounting
with ocfs2_xattr_list_entry(), but it kept using size == 0 to detect
probe mode.

That assumption stops being true once ocfs2_listxattr() finishes the
inline-xattr pass. If the inline names fill the caller buffer exactly,
the block-xattr pass runs with a non-NULL buffer and a remaining size of
zero. ocfs2_xattr_list_entry() then skips the bounds check, keeps
counting block names, and returns a positive size larger than the
supplied buffer.

[FIX]
Detect probe mode by testing whether the destination buffer pointer is
NULL instead of whether the remaining size is zero.

That restores the pre-refactor behavior and matches the OCFS2 getxattr
helpers. Once the remaining buffer reaches zero while more names are
left, the block-xattr pass now returns -ERANGE instead of reporting a
size larger than the allocated list buffer.

## References
- https://git.kernel.org/stable/c/2323084c17370304f49c84b354fe7b3edbb264fe
- https://git.kernel.org/stable/c/2685df8577a38d83b367c8cf52eda9dc286959ff
- https://git.kernel.org/stable/c/46e66fefb83811958127bc9ad736983ec629d82b
- https://git.kernel.org/stable/c/50033ec1350fe68abdc63b950ced7ae57364b77a
- https://git.kernel.org/stable/c/6f702b00b8124c5d3525f19172934544826a114d
- https://git.kernel.org/stable/c/a35a1c2b170b5b578b1b3fecb95694796552af9a
- https://git.kernel.org/stable/c/d12f558e6200b3f47dbef9331ed6d115d2410e59
- https://git.kernel.org/stable/c/d919b905939eda93393e3572900ff70dbad2b47f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53041.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53041
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
