# [H] iommufd: Fix out_fput in iommufd_fault_alloc()

## Summary
Severity: High
Advisory: CVE-2024-56624
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56624
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Fix out_fput in iommufd_fault_alloc()

As fput() calls the file->f_op->release op, where fault obj and ictx are
getting released, there is no need to release these two after fput() one
more time, which would result in imbalanced refcounts:
  refcount_t: decrement hit 0; leaking memory.
  WARNING: CPU: 48 PID: 2369 at lib/refcount.c:31 refcount_warn_saturate+0x60/0x230
  Call trace:
   refcount_warn_saturate+0x60/0x230 (P)
   refcount_warn_saturate+0x60/0x230 (L)
   iommufd_fault_fops_release+0x9c/0xe0 [iommufd]
  ...
  VFS: Close: file count is 0 (f_op=iommufd_fops [iommufd])
  WARNING: CPU: 48 PID: 2369 at fs/open.c:1507 filp_flush+0x3c/0xf0
  Call trace:
   filp_flush+0x3c/0xf0 (P)
   filp_flush+0x3c/0xf0 (L)
   __arm64_sys_close+0x34/0x98
  ...
  imbalanced put on file reference count
  WARNING: CPU: 48 PID: 2369 at fs/file.c:74 __file_ref_put+0x100/0x138
  Call trace:
   __file_ref_put+0x100/0x138 (P)
   __file_ref_put+0x100/0x138 (L)
   __fput_sync+0x4c/0xd0

Drop those two lines to fix the warnings above.

## References
- https://git.kernel.org/stable/c/2b3f30c8edbf9a122ce01f13f0f41fbca5f1d41d
- https://git.kernel.org/stable/c/af7f4780514f850322b2959032ecaa96e4b26472
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56624.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56624
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
