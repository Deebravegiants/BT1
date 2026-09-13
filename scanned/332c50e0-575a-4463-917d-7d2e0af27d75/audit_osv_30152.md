# [H] cifs: fix warning when destroy 'cifs_io_request_pool'

## Summary
Severity: High
Advisory: CVE-2024-50119
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50119
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix warning when destroy 'cifs_io_request_pool'

There's a issue as follows:
WARNING: CPU: 1 PID: 27826 at mm/slub.c:4698 free_large_kmalloc+0xac/0xe0
RIP: 0010:free_large_kmalloc+0xac/0xe0
Call Trace:
 <TASK>
 ? __warn+0xea/0x330
 mempool_destroy+0x13f/0x1d0
 init_cifs+0xa50/0xff0 [cifs]
 do_one_initcall+0xdc/0x550
 do_init_module+0x22d/0x6b0
 load_module+0x4e96/0x5ff0
 init_module_from_file+0xcd/0x130
 idempotent_init_module+0x330/0x620
 __x64_sys_finit_module+0xb3/0x110
 do_syscall_64+0xc1/0x1d0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Obviously, 'cifs_io_request_pool' is not created by mempool_create().
So just use mempool_exit() to revert 'cifs_io_request_pool'.

## References
- https://git.kernel.org/stable/c/2ce1007f42b8a6a0814386cb056feb28dc6d6091
- https://git.kernel.org/stable/c/726416a253c51037636ecc65ad3dada3d02dcaea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50119.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50119
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
