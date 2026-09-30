# [H] iommufd: Fix iopt_access_list_id overwrite bug

## Summary
Severity: High
Advisory: CVE-2024-26786
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26786
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Fix iopt_access_list_id overwrite bug

Syzkaller reported the following WARN_ON:
  WARNING: CPU: 1 PID: 4738 at drivers/iommu/iommufd/io_pagetable.c:1360

  Call Trace:
   iommufd_access_change_ioas+0x2fe/0x4e0
   iommufd_access_destroy_object+0x50/0xb0
   iommufd_object_remove+0x2a3/0x490
   iommufd_object_destroy_user
   iommufd_access_destroy+0x71/0xb0
   iommufd_test_staccess_release+0x89/0xd0
   __fput+0x272/0xb50
   __fput_sync+0x4b/0x60
   __do_sys_close
   __se_sys_close
   __x64_sys_close+0x8b/0x110
   do_syscall_x64

The mismatch between the access pointer in the list and the passed-in
pointer is resulting from an overwrite of access->iopt_access_list_id, in
iopt_add_access(). Called from iommufd_access_change_ioas() when
xa_alloc() succeeds but iopt_calculate_iova_alignment() fails.

Add a new_id in iopt_add_access() and only update iopt_access_list_id when
returning successfully.

## References
- https://git.kernel.org/stable/c/9526a46cc0c378d381560279bea9aa34c84298a0
- https://git.kernel.org/stable/c/aeb004c0cd6958e910123a1607634401009c9539
- https://git.kernel.org/stable/c/f1fb745ee0a6fe43f1d84ec369c7e6af2310fda9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26786.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26786
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
