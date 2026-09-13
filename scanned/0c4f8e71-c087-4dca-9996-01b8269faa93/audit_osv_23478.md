# [H] btrfs: prevent copying too big compressed lzo segment

## Summary
Severity: High
Advisory: CVE-2022-48923
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48923
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.26, >=5.16.0 <5.16.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: prevent copying too big compressed lzo segment

Compressed length can be corrupted to be a lot larger than memory
we have allocated for buffer.
This will cause memcpy in copy_compressed_segment to write outside
of allocated memory.

This mostly results in stuck read syscall but sometimes when using
btrfs send can get #GP

  kernel: general protection fault, probably for non-canonical address 0x841551d5c1000: 0000 [#1] PREEMPT SMP NOPTI
  kernel: CPU: 17 PID: 264 Comm: kworker/u256:7 Tainted: P           OE     5.17.0-rc2-1 #12
  kernel: Workqueue: btrfs-endio btrfs_work_helper [btrfs]
  kernel: RIP: 0010:lzo_decompress_bio (./include/linux/fortify-string.h:225 fs/btrfs/lzo.c:322 fs/btrfs/lzo.c:394) btrfs
  Code starting with the faulting instruction
  ===========================================
     0:*  48 8b 06                mov    (%rsi),%rax              <-- trapping instruction
     3:   48 8d 79 08             lea    0x8(%rcx),%rdi
     7:   48 83 e7 f8             and    $0xfffffffffffffff8,%rdi
     b:   48 89 01                mov    %rax,(%rcx)
     e:   44 89 f0                mov    %r14d,%eax
    11:   48 8b 54 06 f8          mov    -0x8(%rsi,%rax,1),%rdx
  kernel: RSP: 0018:ffffb110812efd50 EFLAGS: 00010212
  kernel: RAX: 0000000000001000 RBX: 000000009ca264c8 RCX: ffff98996e6d8ff8
  kernel: RDX: 0000000000000064 RSI: 000841551d5c1000 RDI: ffffffff9500435d
  kernel: RBP: ffff989a3be856c0 R08: 0000000000000000 R09: 0000000000000000
  kernel: R10: 0000000000000000 R11: 0000000000001000 R12: ffff98996e6d8000
  kernel: R13: 0000000000000008 R14: 0000000000001000 R15: 000841551d5c1000
  kernel: FS:  0000000000000000(0000) GS:ffff98a09d640000(0000) knlGS:0000000000000000
  kernel: CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
  kernel: CR2: 00001e9f984d9ea8 CR3: 000000014971a000 CR4: 00000000003506e0
  kernel: Call Trace:
  kernel:  <TASK>
  kernel: end_compressed_bio_read (fs/btrfs/compression.c:104 fs/btrfs/compression.c:1363 fs/btrfs/compression.c:323) btrfs
  kernel: end_workqueue_fn (fs/btrfs/disk-io.c:1923) btrfs
  kernel: btrfs_work_helper (fs/btrfs/async-thread.c:326) btrfs
  kernel: process_one_work (./arch/x86/include/asm/jump_label.h:27 ./include/linux/jump_label.h:212 ./include/trace/events/workqueue.h:108 kernel/workqueue.c:2312)
  kernel: worker_thread (./include/linux/list.h:292 kernel/workqueue.c:2455)
  kernel: ? process_one_work (kernel/workqueue.c:2397)
  kernel: kthread (kernel/kthread.c:377)
  kernel: ? kthread_complete_and_exit (kernel/kthread.c:332)
  kernel: ret_from_fork (arch/x86/entry/entry_64.S:301)
  kernel:  </TASK>

## References
- https://git.kernel.org/stable/c/741b23a970a79d5d3a1db2d64fa2c7b375a4febb
- https://git.kernel.org/stable/c/8df508b7a44cd8110c726057cd28e8f8116885eb
- https://git.kernel.org/stable/c/e326bd06cdde46df952361456232022298281d16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48923.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
