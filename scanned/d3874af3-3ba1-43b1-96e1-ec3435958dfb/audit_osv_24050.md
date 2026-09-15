# [M] RDMA/core: Fix null-ptr-deref in ib_core_cleanup()

## Summary
Severity: Medium
Advisory: CVE-2022-49925
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49925
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Fix null-ptr-deref in ib_core_cleanup()

KASAN reported a null-ptr-deref error:

  KASAN: null-ptr-deref in range [0x0000000000000118-0x000000000000011f]
  CPU: 1 PID: 379
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
  RIP: 0010:destroy_workqueue+0x2f/0x740
  RSP: 0018:ffff888016137df8 EFLAGS: 00000202
  ...
  Call Trace:
   ib_core_cleanup+0xa/0xa1 [ib_core]
   __do_sys_delete_module.constprop.0+0x34f/0x5b0
   do_syscall_64+0x3a/0x90
   entry_SYSCALL_64_after_hwframe+0x63/0xcd
  RIP: 0033:0x7fa1a0d221b7
  ...

It is because the fail of roce_gid_mgmt_init() is ignored:

 ib_core_init()
   roce_gid_mgmt_init()
     gid_cache_wq = alloc_ordered_workqueue # fail
 ...
 ib_core_cleanup()
   roce_gid_mgmt_cleanup()
     destroy_workqueue(gid_cache_wq)
     # destroy an unallocated wq

Fix this by catching the fail of roce_gid_mgmt_init() in ib_core_init().

## References
- https://git.kernel.org/stable/c/07c0d131cc0fe1f3981a42958fc52d573d303d89
- https://git.kernel.org/stable/c/6b3d5dcb12347f3518308c2c9d2cf72453a3e1e5
- https://git.kernel.org/stable/c/ab817f75e5e0fa58d9be0825da6a7b7d8a1fa1d9
- https://git.kernel.org/stable/c/af8fb5a0600e9ae29950e9422a032c3c22649ee5
- https://git.kernel.org/stable/c/d360e875c011a005628525bf290322058927e7dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49925.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
