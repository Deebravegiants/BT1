# [H] xprtrdma: Fix ep kref imbalance on ADDR_CHANGE

## Summary
Severity: High
Advisory: CVE-2026-72469
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72469
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Fix ep kref imbalance on ADDR_CHANGE

rpcrdma_cm_event_handler() falls through to the disconnected: label
on RDMA_CM_EVENT_ADDR_CHANGE and calls rpcrdma_ep_put() with no
matching get when the event arrives before RDMA_CM_EVENT_ESTABLISHED.
The kref then underflows during connect teardown and
rpcrdma_xprt_disconnect() operates on a freed ep.

Reference counts across a normal connection lifecycle:

    rpcrdma_ep_create()             kref_init     ->1
    rpcrdma_xprt_connect()          ep_get        ->2  (before post_recvs)
    RDMA_CM_EVENT_ESTABLISHED       ep_get        ->3
    RDMA_CM_EVENT_DISCONNECTED      ep_put        ->2
    rpcrdma_xprt_drain()            ep_put        ->1
    rpcrdma_xprt_disconnect() tail  ep_put        ->0  (ep_destroy)

The connect-time get in rpcrdma_xprt_connect(), taken just before
rpcrdma_post_recvs() "while there are outstanding Receives," is
balanced by rpcrdma_xprt_drain. ADDR_CHANGE before ESTABLISHED has
no get to consume, so its put drops the count to 1 and the drain
put then frees the ep while rpcrdma_xprt_disconnect() still holds a
pointer to it.

Fix by dispatching on the prior re_connect_status via xchg(): for
prev == 0 (pre-ESTABLISHED) wake the connect waiter and return with
no put; for prev == 1 call rpcrdma_force_disconnect() and return.
The case-1 arm relies on the subsequent RDMA_CM_EVENT_DISCONNECTED
event -- reliably delivered when rdma_disconnect() is called on a
still-connected cm_id -- to balance the ESTABLISHED get;
rpcrdma_xprt_drain() continues to balance only that connect-time
get. Any other prior value means teardown is already in flight.

## References
- https://git.kernel.org/stable/c/af9b65b29af341932625c4283dc7a23cdb62688a
- https://git.kernel.org/stable/c/cfd1bab66b042da7a778786685125656c695931b
- https://git.kernel.org/stable/c/d0479c2b12974aa188b10d221a5770126b118b6d
- https://git.kernel.org/stable/c/ffc07790539736a5d029f6a3c966b46c529f93a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72469.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72469
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
