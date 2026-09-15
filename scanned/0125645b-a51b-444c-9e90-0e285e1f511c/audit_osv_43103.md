# [C] xfrm: Fix dev use-after-free in xfrm async resumption

## Summary
Severity: Critical
Advisory: CVE-2026-72463
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72463
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: Fix dev use-after-free in xfrm async resumption

xfrm async resumption hold skb->dev refcnt until after transport_finish.
However, xfrm_rcv_cb may modify skb->dev to tunnel dev without taking
device reference, such as vti_rcv_cb. The subsequent async resumption
will decrement the tunnel device's reference count, which lead to uaf
of tunnel dev and refcnt leak of orig dev as below:

unregister_netdevice: waiting for vti1 to become free. Usage count = -2

Stash the original skb->dev to fix refcnt imbalance. The new skb->dev set
by xfrm_rcv_cb can race with device teardown. Extend rcu protection over
xfrm_rcv_cb and transport_finish to prevent races.

## References
- https://git.kernel.org/stable/c/63a30015199912bd5055bead8001b1ae68a67cdb
- https://git.kernel.org/stable/c/8045c0df98d4f14c54e5cb875f1c9c0ce89fe4ff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72463.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72463
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
