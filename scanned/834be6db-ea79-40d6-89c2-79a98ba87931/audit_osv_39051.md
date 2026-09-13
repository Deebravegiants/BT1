# [H] xprtrdma: Decrement re_receiving on the early exit paths

## Summary
Severity: High
Advisory: CVE-2026-43469
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43469
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Decrement re_receiving on the early exit paths

In the event that rpcrdma_post_recvs() fails to create a work request
(due to memory allocation failure, say) or otherwise exits early, we
should decrement ep->re_receiving before returning. Otherwise we will
hang in rpcrdma_xprt_drain() as re_receiving will never reach zero and
the completion will never be triggered.

On a system with high memory pressure, this can appear as the following
hung task:

    INFO: task kworker/u385:17:8393 blocked for more than 122 seconds.
          Tainted: G S          E       6.19.0 #3
    "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
    task:kworker/u385:17 state:D stack:0     pid:8393  tgid:8393  ppid:2      task_flags:0x4248060 flags:0x00080000
    Workqueue: xprtiod xprt_autoclose [sunrpc]
    Call Trace:
     <TASK>
     __schedule+0x48b/0x18b0
     ? ib_post_send_mad+0x247/0xae0 [ib_core]
     schedule+0x27/0xf0
     schedule_timeout+0x104/0x110
     __wait_for_common+0x98/0x180
     ? __pfx_schedule_timeout+0x10/0x10
     wait_for_completion+0x24/0x40
     rpcrdma_xprt_disconnect+0x444/0x460 [rpcrdma]
     xprt_rdma_close+0x12/0x40 [rpcrdma]
     xprt_autoclose+0x5f/0x120 [sunrpc]
     process_one_work+0x191/0x3e0
     worker_thread+0x2e3/0x420
     ? __pfx_worker_thread+0x10/0x10
     kthread+0x10d/0x230
     ? __pfx_kthread+0x10/0x10
     ret_from_fork+0x273/0x2b0
     ? __pfx_kthread+0x10/0x10
     ret_from_fork_asm+0x1a/0x30

## References
- https://git.kernel.org/stable/c/49f53ee4e25297d886f14e31f355ad1c2735ddfb
- https://git.kernel.org/stable/c/74c39a47856bddcde7874f2196a00143b5cd0af9
- https://git.kernel.org/stable/c/7b6275c80a0c81c5f8943272292dfe67730ce849
- https://git.kernel.org/stable/c/7ea69259a60a364f56cf4aa9e2eafb588d1c762b
- https://git.kernel.org/stable/c/8127b5fec04757c2a41ed65bca0b3266968efd3b
- https://git.kernel.org/stable/c/8cb6b5d8296b1f99a8d36849901ebabfe3f749db
- https://git.kernel.org/stable/c/dc3ebd7e2d73dbd4d317785735ffa6c4a6384ddf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43469.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43469
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
