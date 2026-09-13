# [H] RDMA/rxe: Fix slab-use-after-free Read in rxe_queue_cleanup bug

## Summary
Severity: High
Advisory: CVE-2025-38024
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38024
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.184, >=5.16.0 <6.1.140, >=6.2.0 <6.6.92, >=6.7.0 <6.12.30, >=6.13.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix slab-use-after-free Read in rxe_queue_cleanup bug

Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x7d/0xa0 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378 [inline]
 print_report+0xcf/0x610 mm/kasan/report.c:489
 kasan_report+0xb5/0xe0 mm/kasan/report.c:602
 rxe_queue_cleanup+0xd0/0xe0 drivers/infiniband/sw/rxe/rxe_queue.c:195
 rxe_cq_cleanup+0x3f/0x50 drivers/infiniband/sw/rxe/rxe_cq.c:132
 __rxe_cleanup+0x168/0x300 drivers/infiniband/sw/rxe/rxe_pool.c:232
 rxe_create_cq+0x22e/0x3a0 drivers/infiniband/sw/rxe/rxe_verbs.c:1109
 create_cq+0x658/0xb90 drivers/infiniband/core/uverbs_cmd.c:1052
 ib_uverbs_create_cq+0xc7/0x120 drivers/infiniband/core/uverbs_cmd.c:1095
 ib_uverbs_write+0x969/0xc90 drivers/infiniband/core/uverbs_main.c:679
 vfs_write fs/read_write.c:677 [inline]
 vfs_write+0x26a/0xcc0 fs/read_write.c:659
 ksys_write+0x1b8/0x200 fs/read_write.c:731
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xaa/0x1b0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

In the function rxe_create_cq, when rxe_cq_from_init fails, the function
rxe_cleanup will be called to handle the allocated resources. In fact,
some memory resources have already been freed in the function
rxe_cq_from_init. Thus, this problem will occur.

The solution is to let rxe_cleanup do all the work.

## References
- https://git.kernel.org/stable/c/16c45ced0b3839d3eee72a86bb172bef6cf58980
- https://git.kernel.org/stable/c/336edd6b0f5b7fbffc3e065285610624f59e88df
- https://git.kernel.org/stable/c/3a3b73e135e3bd18423d0baa72571319c7feb759
- https://git.kernel.org/stable/c/52daccfc3fa68ee1902d52124921453d7a335591
- https://git.kernel.org/stable/c/7c7c80c32e00665234e373ab03fe82f5c5c2c230
- https://git.kernel.org/stable/c/ee4c5a2a38596d548566560c0c022ab797e6f71a
- https://git.kernel.org/stable/c/f81b33582f9339d2dc17c69b92040d3650bb4bae
- https://git.kernel.org/stable/c/f8f470e3a757425a8f98fb9a5991e3cf62fc7134
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38024.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38024
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
