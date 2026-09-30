# [H] RDMA/irdma: Fix drain SQ hang with no completion

## Summary
Severity: High
Advisory: CVE-2022-48694
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48694
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix drain SQ hang with no completion

SW generated completions for outstanding WRs posted on SQ
after QP is in error target the wrong CQ. This causes the
ib_drain_sq to hang with no completion.

Fix this to generate completions on the right CQ.

[  863.969340] INFO: task kworker/u52:2:671 blocked for more than 122 seconds.
[  863.979224]       Not tainted 5.14.0-130.el9.x86_64 #1
[  863.986588] "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
[  863.996997] task:kworker/u52:2   state:D stack:    0 pid:  671 ppid:     2 flags:0x00004000
[  864.007272] Workqueue: xprtiod xprt_autoclose [sunrpc]
[  864.014056] Call Trace:
[  864.017575]  __schedule+0x206/0x580
[  864.022296]  schedule+0x43/0xa0
[  864.026736]  schedule_timeout+0x115/0x150
[  864.032185]  __wait_for_common+0x93/0x1d0
[  864.037717]  ? usleep_range_state+0x90/0x90
[  864.043368]  __ib_drain_sq+0xf6/0x170 [ib_core]
[  864.049371]  ? __rdma_block_iter_next+0x80/0x80 [ib_core]
[  864.056240]  ib_drain_sq+0x66/0x70 [ib_core]
[  864.062003]  rpcrdma_xprt_disconnect+0x82/0x3b0 [rpcrdma]
[  864.069365]  ? xprt_prepare_transmit+0x5d/0xc0 [sunrpc]
[  864.076386]  xprt_rdma_close+0xe/0x30 [rpcrdma]
[  864.082593]  xprt_autoclose+0x52/0x100 [sunrpc]
[  864.088718]  process_one_work+0x1e8/0x3c0
[  864.094170]  worker_thread+0x50/0x3b0
[  864.099109]  ? rescuer_thread+0x370/0x370
[  864.104473]  kthread+0x149/0x170
[  864.109022]  ? set_kthread_struct+0x40/0x40
[  864.114713]  ret_from_fork+0x22/0x30

## References
- https://git.kernel.org/stable/c/14d148401c5202fec3a071e24785481d540b22c3
- https://git.kernel.org/stable/c/5becc531a3fa8da75158a8993f56cc3e0717716e
- https://git.kernel.org/stable/c/ead54ced6321099978d30d62dc49c282a6e70574
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48694.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
