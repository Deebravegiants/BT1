# [C] net/smc: fix NULL dereference and UAF in smc_tcp_syn_recv_sock()

## Summary
Severity: Critical
Advisory: CVE-2026-23450
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23450
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.167, >=5.18.0 <6.6.130, >=6.2.0 <6.12.78, >=6.7.0 <6.18.20, >=6.13.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix NULL dereference and UAF in smc_tcp_syn_recv_sock()

Syzkaller reported a panic in smc_tcp_syn_recv_sock() [1].

smc_tcp_syn_recv_sock() is called in the TCP receive path
(softirq) via icsk_af_ops->syn_recv_sock on the clcsock (TCP
listening socket). It reads sk_user_data to get the smc_sock
pointer. However, when the SMC listen socket is being closed
concurrently, smc_close_active() sets clcsock->sk_user_data
to NULL under sk_callback_lock, and then the smc_sock itself
can be freed via sock_put() in smc_release().

This leads to two issues:

1) NULL pointer dereference: sk_user_data is NULL when
   accessed.
2) Use-after-free: sk_user_data is read as non-NULL, but the
   smc_sock is freed before its fields (e.g., queued_smc_hs,
   ori_af_ops) are accessed.

The race window looks like this (the syzkaller crash [1]
triggers via the SYN cookie path: tcp_get_cookie_sock() ->
smc_tcp_syn_recv_sock(), but the normal tcp_check_req() path
has the same race):

  CPU A (softirq)              CPU B (process ctx)

  tcp_v4_rcv()
    TCP_NEW_SYN_RECV:
    sk = req->rsk_listener
    sock_hold(sk)
    /* No lock on listener */
                               smc_close_active():
                                 write_lock_bh(cb_lock)
                                 sk_user_data = NULL
                                 write_unlock_bh(cb_lock)
                                 ...
                                 smc_clcsock_release()
                                 sock_put(smc->sk) x2
                                   -> smc_sock freed!
    tcp_check_req()
      smc_tcp_syn_recv_sock():
        smc = user_data(sk)
          -> NULL or dangling
        smc->queued_smc_hs
          -> crash!

Note that the clcsock and smc_sock are two independent objects
with separate refcounts. TCP stack holds a reference on the
clcsock, which keeps it alive, but this does NOT prevent the
smc_sock from being freed.

Fix this by using RCU and refcount_inc_not_zero() to safely
access smc_sock. Since smc_tcp_syn_recv_sock() is called in
the TCP three-way handshake path, taking read_lock_bh on
sk_callback_lock is too heavy and would not survive a SYN
flood attack. Using rcu_read_lock() is much more lightweight.

- Set SOCK_RCU_FREE on the SMC listen socket so that
  smc_sock freeing is deferred until after the RCU grace
  period. This guarantees the memory is still valid when
  accessed inside rcu_read_lock().
- Use rcu_read_lock() to protect reading sk_user_data.
- Use refcount_inc_not_zero(&smc->sk.sk_refcnt) to pin the
  smc_sock. If the refcount has already reached zero (close
  path completed), it returns false and we bail out safely.

Note: smc_hs_congested() has a similar lockless read of
sk_user_data without rcu_read_lock(), but it only checks for
NULL and accesses the global smc_hs_wq, never dereferencing
any smc_sock field, so it is not affected.

Reproducer was verified with mdelay injection and smc_run,
the issue no longer occurs with this patch applied.

[1] https://syzkaller.appspot.com/bug?extid=827ae2bfb3a3529333e9

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1e4f873879e075bbd4eb1c644d6933303ac5eba4
- https://git.kernel.org/stable/c/1fab5ece76fb42a761178dcd0ebcbf578377b0dd
- https://git.kernel.org/stable/c/6d5e4538364b9ceb1ac2941a4deb86650afb3538
- https://git.kernel.org/stable/c/cadf3da46c15523fba90d80c9955f536ee3b4023
- https://git.kernel.org/stable/c/f00fc26c8a06442b225a350fe000c0a11483e6a3
- https://git.kernel.org/stable/c/f315277856caeafcd996c2611afc085ca2d53275
- https://git.kernel.org/stable/c/fd7579f0a2c84ba8a7d4f206201b50dc8ddf90c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23450
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
