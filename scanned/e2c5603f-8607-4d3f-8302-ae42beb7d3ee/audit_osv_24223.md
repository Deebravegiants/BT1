# [H] block, bfq: fix possible uaf for 'bfqq->bic'

## Summary
Severity: High
Advisory: CVE-2022-50488
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2022-50488
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.175, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=5.19.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

block, bfq: fix possible uaf for 'bfqq->bic'

Our test report a uaf for 'bfqq->bic' in 5.10:

==================================================================
BUG: KASAN: use-after-free in bfq_select_queue+0x378/0xa30

CPU: 6 PID: 2318352 Comm: fsstress Kdump: loaded Not tainted 5.10.0-60.18.0.50.h602.kasan.eulerosv2r11.x86_64 #1
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.12.1-0-ga5cab58-20220320_160524-szxrtosci10000 04/01/2014
Call Trace:
 bfq_select_queue+0x378/0xa30
 bfq_dispatch_request+0xe8/0x130
 blk_mq_do_dispatch_sched+0x62/0xb0
 __blk_mq_sched_dispatch_requests+0x215/0x2a0
 blk_mq_sched_dispatch_requests+0x8f/0xd0
 __blk_mq_run_hw_queue+0x98/0x180
 __blk_mq_delay_run_hw_queue+0x22b/0x240
 blk_mq_run_hw_queue+0xe3/0x190
 blk_mq_sched_insert_requests+0x107/0x200
 blk_mq_flush_plug_list+0x26e/0x3c0
 blk_finish_plug+0x63/0x90
 __iomap_dio_rw+0x7b5/0x910
 iomap_dio_rw+0x36/0x80
 ext4_dio_read_iter+0x146/0x190 [ext4]
 ext4_file_read_iter+0x1e2/0x230 [ext4]
 new_sync_read+0x29f/0x400
 vfs_read+0x24e/0x2d0
 ksys_read+0xd5/0x1b0
 do_syscall_64+0x33/0x40
 entry_SYSCALL_64_after_hwframe+0x61/0xc6

Commit 3bc5e683c67d ("bfq: Split shared queues on move between cgroups")
changes that move process to a new cgroup will allocate a new bfqq to
use, however, the old bfqq and new bfqq can point to the same bic:

1) Initial state, two process with io in the same cgroup.

Process 1       Process 2
 (BIC1)          (BIC2)
  |  Λ            |  Λ
  |  |            |  |
  V  |            V  |
  bfqq1           bfqq2

2) bfqq1 is merged to bfqq2.

Process 1       Process 2
 (BIC1)          (BIC2)
  |               |
   \-------------\|
                  V
  bfqq1           bfqq2(coop)

3) Process 1 exit, then issue new io(denoce IOA) from Process 2.

 (BIC2)
  |  Λ
  |  |
  V  |
  bfqq2(coop)

4) Before IOA is completed, move Process 2 to another cgroup and issue io.

Process 2
 (BIC2)
   Λ
   |\--------------\
   |                V
  bfqq2           bfqq3

Now that BIC2 points to bfqq3, while bfqq2 and bfqq3 both point to BIC2.
If all the requests are completed, and Process 2 exit, BIC2 will be
freed while there is no guarantee that bfqq2 will be freed before BIC2.

Fix the problem by clearing bfqq->bic while bfqq is detached from bic.

## References
- https://git.kernel.org/stable/c/094f3d9314d67691cb21ba091c1b528f6e3c4893
- https://git.kernel.org/stable/c/5533742c7cb1bc9b1f0bf401cc397d44a3a9e07a
- https://git.kernel.org/stable/c/64dc8c732f5c2b406cc752e6aaa1bd5471159cab
- https://git.kernel.org/stable/c/761564d93c8265f65543acf0a576b32d66bfa26a
- https://git.kernel.org/stable/c/b22fd72bfebda3956efc4431b60ddfc0a51e03e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50488.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50488
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
