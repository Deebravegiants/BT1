# [M] iommufd: Fix protection fault in iommufd_test_syz_conv_iova

## Summary
Severity: Medium
Advisory: CVE-2024-26785
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26785
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.55, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Fix protection fault in iommufd_test_syz_conv_iova

Syzkaller reported the following bug:

  general protection fault, probably for non-canonical address 0xdffffc0000000038: 0000 [#1] SMP KASAN
  KASAN: null-ptr-deref in range [0x00000000000001c0-0x00000000000001c7]
  Call Trace:
   lock_acquire
   lock_acquire+0x1ce/0x4f0
   down_read+0x93/0x4a0
   iommufd_test_syz_conv_iova+0x56/0x1f0
   iommufd_test_access_rw.isra.0+0x2ec/0x390
   iommufd_test+0x1058/0x1e30
   iommufd_fops_ioctl+0x381/0x510
   vfs_ioctl
   __do_sys_ioctl
   __se_sys_ioctl
   __x64_sys_ioctl+0x170/0x1e0
   do_syscall_x64
   do_syscall_64+0x71/0x140

This is because the new iommufd_access_change_ioas() sets access->ioas to
NULL during its process, so the lock might be gone in a concurrent racing
context.

Fix this by doing the same access->ioas sanity as iommufd_access_rw() and
iommufd_access_pin_pages() functions do.

## References
- https://git.kernel.org/stable/c/cf7c2789822db8b5efa34f5ebcf1621bc0008d48
- https://git.kernel.org/stable/c/fc719ecbca45c9c046640d72baddba3d83e0bc0b
- https://git.kernel.org/stable/c/fd4d5cd7a2e8f08357c9bfc0905957cffe8ce568
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26785.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26785
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
