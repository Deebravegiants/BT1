# [H] IB/mad: Don't call to function that might sleep while in atomic context

## Summary
Severity: High
Advisory: CVE-2022-50472
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2022-50472
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.258, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/mad: Don't call to function that might sleep while in atomic context

Tracepoints are not allowed to sleep, as such the following splat is
generated due to call to ib_query_pkey() in atomic context.

WARNING: CPU: 0 PID: 1888000 at kernel/trace/ring_buffer.c:2492 rb_commit+0xc1/0x220
CPU: 0 PID: 1888000 Comm: kworker/u9:0 Kdump: loaded Tainted: G           OE    --------- -  - 4.18.0-305.3.1.el8.x86_64 #1
 Hardware name: Red Hat KVM, BIOS 1.13.0-2.module_el8.3.0+555+a55c8938 04/01/2014
 Workqueue: ib-comp-unb-wq ib_cq_poll_work [ib_core]
 RIP: 0010:rb_commit+0xc1/0x220
 RSP: 0000:ffffa8ac80f9bca0 EFLAGS: 00010202
 RAX: ffff8951c7c01300 RBX: ffff8951c7c14a00 RCX: 0000000000000246
 RDX: ffff8951c707c000 RSI: ffff8951c707c57c RDI: ffff8951c7c14a00
 RBP: 0000000000000000 R08: 0000000000000000 R09: 0000000000000000
 R10: ffff8951c7c01300 R11: 0000000000000001 R12: 0000000000000246
 R13: 0000000000000000 R14: ffffffff964c70c0 R15: 0000000000000000
 FS:  0000000000000000(0000) GS:ffff8951fbc00000(0000) knlGS:0000000000000000
 CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 00007f20e8f39010 CR3: 000000002ca10005 CR4: 0000000000170ef0
 Call Trace:
  ring_buffer_unlock_commit+0x1d/0xa0
  trace_buffer_unlock_commit_regs+0x3b/0x1b0
  trace_event_buffer_commit+0x67/0x1d0
  trace_event_raw_event_ib_mad_recv_done_handler+0x11c/0x160 [ib_core]
  ib_mad_recv_done+0x48b/0xc10 [ib_core]
  ? trace_event_raw_event_cq_poll+0x6f/0xb0 [ib_core]
  __ib_process_cq+0x91/0x1c0 [ib_core]
  ib_cq_poll_work+0x26/0x80 [ib_core]
  process_one_work+0x1a7/0x360
  ? create_worker+0x1a0/0x1a0
  worker_thread+0x30/0x390
  ? create_worker+0x1a0/0x1a0
  kthread+0x116/0x130
  ? kthread_flush_work_fn+0x10/0x10
  ret_from_fork+0x35/0x40
 ---[ end trace 78ba8509d3830a16 ]---

## References
- https://git.kernel.org/stable/c/47e31b86edff36f2d26cbc88ce695d98ff804178
- https://git.kernel.org/stable/c/5c20311d76cbaeb7ed2ecf9c8b8322f8fc4a7ae3
- https://git.kernel.org/stable/c/cea70a572c0cb9728d728cfebe7d5bd485e97513
- https://git.kernel.org/stable/c/d45e6ccb8e98d8339631f32984d345a663e74ce2
- https://git.kernel.org/stable/c/fa8a2f3be78e4585996bcf4c15e4504441a4c7a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50472.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50472
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
