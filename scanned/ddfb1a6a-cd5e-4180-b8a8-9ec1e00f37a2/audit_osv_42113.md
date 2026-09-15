# [C] net/smc: fix UAF in smc_cdc_rx_handler() by pinning the socket

## Summary
Severity: Critical
Advisory: CVE-2026-64541
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64541
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix UAF in smc_cdc_rx_handler() by pinning the socket

smc_cdc_rx_handler() looks up the connection by token under the link
group's conns_lock, drops the lock, and then dereferences conn and the
smc_sock derived from it, ending in sock_hold(&smc->sk) inside
smc_cdc_msg_recv(). No reference is held across the lock release.

The only reference pinning the socket while the connection is
discoverable in the link group is taken in smc_lgr_register_conn()
(sock_hold) and dropped in __smc_lgr_unregister_conn() (sock_put), both
under conns_lock. Once the handler drops conns_lock, a concurrent
close() -> smc_release() -> smc_conn_free() -> smc_lgr_unregister_conn()
can drop that reference and free the smc_sock, so the handler's later
sock_hold() runs on freed memory:

  WARNING: lib/refcount.c:25 at refcount_warn_saturate
  Workqueue: rxe_wq do_work
   refcount_warn_saturate (lib/refcount.c:25)
   smc_cdc_msg_recv (net/smc/smc_cdc.c:430)
   smc_cdc_rx_handler (net/smc/smc_cdc.c:502)
   smc_wr_rx_tasklet_fn (net/smc/smc_wr.c:445)
   tasklet_action_common (kernel/softirq.c:938)
   handle_softirqs (kernel/softirq.c:622)
  Kernel panic - not syncing: panic_on_warn set

Only SMC-R is affected. The SMC-D receive tasklet is stopped by
tasklet_kill(&conn->rx_tsklet) in smc_conn_free() before the connection
is unregistered, so it cannot run concurrently with the free.

Take the socket reference while still holding conns_lock, so the
registration reference can no longer be the last one, and drop it once
the handler is done.

## References
- https://git.kernel.org/stable/c/1951bffbc6493ec34cff3956b29d4bc6606904a6
- https://git.kernel.org/stable/c/3bfb96d9bc6a7ed0b99c7db329cc2e22a28d84bb
- https://git.kernel.org/stable/c/472e9d7c0d5b03be3ff91ff941f57da822b031bc
- https://git.kernel.org/stable/c/647b19e5cc145a2f1f685ae8ff3805a17356888c
- https://git.kernel.org/stable/c/8145b432136285e01091815b48ceb2dae261f262
- https://git.kernel.org/stable/c/8de4f665d0febfb92803dece377791a563fc7041
- https://git.kernel.org/stable/c/9d160b35cc34a2ba8229d07651468a7848325135
- https://git.kernel.org/stable/c/ce5aa8084329351086894aa34d77e40301d5bd3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64541.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64541
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
