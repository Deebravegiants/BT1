# [M] ext4: add reserved GDT blocks check

## Summary
Severity: Medium
Advisory: CVE-2022-49707
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49707
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.9.320, >=4.10.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: add reserved GDT blocks check

We capture a NULL pointer issue when resizing a corrupt ext4 image which
is freshly clear resize_inode feature (not run e2fsck). It could be
simply reproduced by following steps. The problem is because of the
resize_inode feature was cleared, and it will convert the filesystem to
meta_bg mode in ext4_resize_fs(), but the es->s_reserved_gdt_blocks was
not reduced to zero, so could we mistakenly call reserve_backup_gdb()
and passing an uninitialized resize_inode to it when adding new group
descriptors.

 mkfs.ext4 /dev/sda 3G
 tune2fs -O ^resize_inode /dev/sda #forget to run requested e2fsck
 mount /dev/sda /mnt
 resize2fs /dev/sda 8G

 ========
 BUG: kernel NULL pointer dereference, address: 0000000000000028
 CPU: 19 PID: 3243 Comm: resize2fs Not tainted 5.18.0-rc7-00001-gfde086c5ebfd #748
 ...
 RIP: 0010:ext4_flex_group_add+0xe08/0x2570
 ...
 Call Trace:
  <TASK>
  ext4_resize_fs+0xbec/0x1660
  __ext4_ioctl+0x1749/0x24e0
  ext4_ioctl+0x12/0x20
  __x64_sys_ioctl+0xa6/0x110
  do_syscall_64+0x3b/0x90
  entry_SYSCALL_64_after_hwframe+0x44/0xae
 RIP: 0033:0x7f2dd739617b
 ========

The fix is simple, add a check in ext4_resize_begin() to make sure that
the es->s_reserved_gdt_blocks is zero when the resize_inode feature is
disabled.

## References
- https://git.kernel.org/stable/c/0dc2fca8e4f9ac4a40e8424a10163369cca0cc06
- https://git.kernel.org/stable/c/33b1bba31f4c784d33d2c2517964bdccdc9204cd
- https://git.kernel.org/stable/c/7c921328ac760bba780bdace41f4cd045f7f1405
- https://git.kernel.org/stable/c/af75c481a2e45e70f62f5942c93695e95bf7bd21
- https://git.kernel.org/stable/c/b55c3cd102a6f48b90e61c44f7f3dda8c290c694
- https://git.kernel.org/stable/c/b9747263b13e5290ac4d63bec47e38f701303cad
- https://git.kernel.org/stable/c/bfd004a1d3a062aac300523d406ac1f3e5f1a82c
- https://git.kernel.org/stable/c/fba54289176702a7caac0b64738406775817f451
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49707.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49707
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
