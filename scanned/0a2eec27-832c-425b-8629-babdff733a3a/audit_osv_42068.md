# [H] audit: Fix data races of skb_queue_len() readers on audit_queue

## Summary
Severity: High
Advisory: CVE-2026-64435
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64435
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

audit: Fix data races of skb_queue_len() readers on audit_queue

Multiple readers access audit_queue.qlen via skb_queue_len() without
holding the queue lock or using READ_ONCE(), while kauditd writes to
this field via the skb_dequeue() → __skb_unlink() path with WRITE_ONCE()
protected by a spinlock. This constitutes data races.

All affected skb_queue_len(&audit_queue) call sites:
  - kauditd_thread() wait_event_freezable() condition
  - audit_receive_msg() AUDIT_GET handler (s.backlog assignment)
  - audit_receive() backlog check
  - audit_log_start() backlog check and pr_warn()

KCSAN reports the following conflicting access pattern (one example):
==================================================================
BUG: KCSAN: data-race in audit_log_start / skb_dequeue

write (marked) to 0xffffffff8512ee20 of 4 bytes by task 661 on cpu 57:
 skb_dequeue+0x70/0xf0
 kauditd_send_queue+0x71/0x220
 kauditd_thread+0x1cb/0x430
 kthread+0x1c2/0x210
 ret_from_fork+0x162/0x1a0
 ret_from_fork_asm+0x1a/0x30

read to 0xffffffff8512ee20 of 4 bytes by task 36586 on cpu 1:
 audit_log_start+0x2a0/0x6b0
 audit_core_dumps+0x64/0xa0
 do_coredump+0x14b/0x1260
 get_signal+0xeb2/0xf70
 arch_do_signal_or_restart+0x41/0x170
 exit_to_user_mode_loop+0xa2/0x1c0
 do_syscall_64+0x1a3/0x1c0
 entry_SYSCALL_64_after_hwframe+0x76/0xe0

value changed: 0x00000001 -> 0x00000000
==================================================================

Resolve the race by switching to lockless helper skb_queue_len_lockless(),
which internally uses READ_ONCE() and properly pairs with the WRITE_ONCE()
write accesses already present on the writer side.

[PM: line length tweak]

## References
- https://git.kernel.org/stable/c/69f98fff30bdaa72b0cb0e7e078ab6456a0a59b0
- https://git.kernel.org/stable/c/7ff42312ccde549f8c698723822c7db35107a39b
- https://git.kernel.org/stable/c/a3d85dec60bb0622360fc176b2a51abdbe2ff0ad
- https://git.kernel.org/stable/c/b35597bdae1a5d8395da4b9baa993b9b71f74d68
- https://git.kernel.org/stable/c/c5186201fa7030289cc4fe23fae87a3fcb566856
- https://git.kernel.org/stable/c/c9a71daaecb2fb1d8c704545cc0b1c920b9bf5d7
- https://git.kernel.org/stable/c/e575dabb805252e3113fdc3f56f6ecacfde422d0
- https://git.kernel.org/stable/c/fe997a84a385f840b593ead92e575503a5046cee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64435.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
