# [H] tipc: fix a null-ptr-deref in tipc_topsrv_accept

## Summary
Severity: High
Advisory: CVE-2022-50555
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2022-50555
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.264, >=4.20.0 <5.4.223, >=5.5.0 <5.10.153, >=5.11.0 <5.15.77, >=5.16.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix a null-ptr-deref in tipc_topsrv_accept

syzbot found a crash in tipc_topsrv_accept:

  KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
  Workqueue: tipc_rcv tipc_topsrv_accept
  RIP: 0010:kernel_accept+0x22d/0x350 net/socket.c:3487
  Call Trace:
   <TASK>
   tipc_topsrv_accept+0x197/0x280 net/tipc/topsrv.c:460
   process_one_work+0x991/0x1610 kernel/workqueue.c:2289
   worker_thread+0x665/0x1080 kernel/workqueue.c:2436
   kthread+0x2e4/0x3a0 kernel/kthread.c:376
   ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:306

It was caused by srv->listener that might be set to null by
tipc_topsrv_stop() in net .exit whereas it's still used in
tipc_topsrv_accept() worker.

srv->listener is protected by srv->idr_lock in tipc_topsrv_stop(), so add
a check for srv->listener under srv->idr_lock in tipc_topsrv_accept() to
avoid the null-ptr-deref. To ensure the lsock is not released during the
tipc_topsrv_accept(), move sock_release() after tipc_topsrv_work_stop()
where it's waiting until the tipc_topsrv_accept worker to be done.

Note that sk_callback_lock is used to protect sk->sk_user_data instead of
srv->listener, and it should check srv in tipc_topsrv_listener_data_ready()
instead. This also ensures that no more tipc_topsrv_accept worker will be
started after tipc_conn_close() is called in tipc_topsrv_stop() where it
sets sk->sk_user_data to null.

## References
- https://git.kernel.org/stable/c/24b129aed8730e48f47d852d58d76825ab6f407c
- https://git.kernel.org/stable/c/32a3d4660b34ce49ac0162338ebe362098e2f5df
- https://git.kernel.org/stable/c/7a939503fc32bff4ed60800b73ff7fbb4aea2142
- https://git.kernel.org/stable/c/82cb4e4612c633a9ce320e1773114875604a3cce
- https://git.kernel.org/stable/c/ce69bdac2310152bb70845024d5d704c52aabfc3
- https://git.kernel.org/stable/c/cedb41664e27b2cae7e21487f1bee22dcd84037d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50555.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50555
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
