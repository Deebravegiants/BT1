# [M] scsi: mpi3mr: Fix possible crash when setting up bsg fails

## Summary
Severity: Medium
Advisory: CVE-2025-21723
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21723
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Fix possible crash when setting up bsg fails

If bsg_setup_queue() fails, the bsg_queue is assigned a non-NULL value.
Consequently, in mpi3mr_bsg_exit(), the condition "if(!mrioc->bsg_queue)"
will not be satisfied, preventing execution from entering
bsg_remove_queue(), which could lead to the following crash:

BUG: kernel NULL pointer dereference, address: 000000000000041c
Call Trace:
  <TASK>
  mpi3mr_bsg_exit+0x1f/0x50 [mpi3mr]
  mpi3mr_remove+0x6f/0x340 [mpi3mr]
  pci_device_remove+0x3f/0xb0
  device_release_driver_internal+0x19d/0x220
  unbind_store+0xa4/0xb0
  kernfs_fop_write_iter+0x11f/0x200
  vfs_write+0x1fc/0x3e0
  ksys_write+0x67/0xe0
  do_syscall_64+0x38/0x80
  entry_SYSCALL_64_after_hwframe+0x78/0xe2

## References
- https://git.kernel.org/stable/c/19b248069d1b1424982723a2bf3941ad864d5204
- https://git.kernel.org/stable/c/295006f6e8c17212d3098811166e29627d19e05c
- https://git.kernel.org/stable/c/832b8f95a2832321b8200ae478ed988b25faaef4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21723.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21723
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
