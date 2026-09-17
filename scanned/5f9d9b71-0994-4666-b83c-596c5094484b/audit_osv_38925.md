# [C] net: ioam6: fix OOB and missing lock

## Summary
Severity: Critical
Advisory: CVE-2026-43083
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43083
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ioam6: fix OOB and missing lock

When trace->type.bit6 is set:

    if (trace->type.bit6) {
        ...
        queue = skb_get_tx_queue(dev, skb);
        qdisc = rcu_dereference(queue->qdisc);

This code can lead to an out-of-bounds access of the dev->_tx[] array
when is_input is true. In such a case, the packet is on the RX path and
skb->queue_mapping contains the RX queue index of the ingress device. If
the ingress device has more RX queues than the egress device (dev) has
TX queues, skb_get_queue_mapping(skb) will exceed dev->num_tx_queues.
Add a check to avoid this situation since skb_get_tx_queue() does not
clamp the index. This issue has also revealed that per queue visibility
cannot be accurate and will be replaced later as a new feature.

While at it, add missing lock around qdisc_qstats_qlen_backlog(). The
function __ioam6_fill_trace_data() is called from both softirq and
process contexts, hence the use of spin_lock_bh() here.

## References
- https://git.kernel.org/stable/c/6d1d9ed9b409e0662241e3d245d574a18f643494
- https://git.kernel.org/stable/c/95a1334748c95dd15546056280ade0c4b8dd7b78
- https://git.kernel.org/stable/c/b30b1675aa2bcf0491fd3830b051df4e08a7c8ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43083.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
