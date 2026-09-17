# [M] scsi: target: core: Fix null-ptr-deref in target_alloc_device()

## Summary
Severity: Medium
Advisory: CVE-2024-50153
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50153
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.229, >=5.11.0 <6.1.115, >=5.16.0 <6.6.59, >=6.2.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: core: Fix null-ptr-deref in target_alloc_device()

There is a null-ptr-deref issue reported by KASAN:

BUG: KASAN: null-ptr-deref in target_alloc_device+0xbc4/0xbe0 [target_core_mod]
...
 kasan_report+0xb9/0xf0
 target_alloc_device+0xbc4/0xbe0 [target_core_mod]
 core_dev_setup_virtual_lun0+0xef/0x1f0 [target_core_mod]
 target_core_init_configfs+0x205/0x420 [target_core_mod]
 do_one_initcall+0xdd/0x4e0
...
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

In target_alloc_device(), if allocing memory for dev queues fails, then
dev will be freed by dev->transport->free_device(), but dev->transport
is not initialized at that time, which will lead to a null pointer
reference problem.

Fixing this bug by freeing dev with hba->backend->ops->free_device().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/14a6a2adb440e4ae97bee73b2360946bd033dadd
- https://git.kernel.org/stable/c/39e02fa90323243187c91bb3e8f2f5f6a9aacfc7
- https://git.kernel.org/stable/c/895ab729425ef9bf3b6d2f8d0853abe64896f314
- https://git.kernel.org/stable/c/8c1e6717f60d31f8af3937c23c4f1498529584e1
- https://git.kernel.org/stable/c/b80e9bc85bd9af378e7eac83e15dd129557bbdb6
- https://git.kernel.org/stable/c/fca6caeb4a61d240f031914413fcc69534f6dc03
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50153.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50153
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
