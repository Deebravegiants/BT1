# [H] netfilter: nf_queue: hold bridge skb->dev while queued

## Summary
Severity: High
Advisory: CVE-2026-52912
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52912
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.259, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_queue: hold bridge skb->dev while queued

br_pass_frame_up() rewrites skb->dev from the ingress port to the bridge
master before queueing bridge LOCAL_IN packets. NFQUEUE only holds
references on state.in/out and bridge physdevs, so a queued bridge
packet can retain a freed bridge master in skb->dev until reinjection.

When the verdict is reinjected later, br_netif_receive_skb() re-enters
the receive path with skb->dev still pointing at the freed bridge master,
triggering a use-after-free.

Store skb->dev in the queue entry, hold a reference on it for the queue
lifetime, and use the saved device when dropping queued packets during
NETDEV_DOWN handling.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/15d464265120ab9818bd673af301deee09bedab2
- https://git.kernel.org/stable/c/19924bdd8a45ebc72a7b84c57fd63057d1dc75ac
- https://git.kernel.org/stable/c/1e5e20031c5eee8d2e490a90ff4d6a2feecfc3be
- https://git.kernel.org/stable/c/3823c27099cfe2482299065814adbaa771be9644
- https://git.kernel.org/stable/c/3fb0f5c0f64162a8c3f25616a4f1e340b921737f
- https://git.kernel.org/stable/c/950d809f154dca04e5fbe5d3c8b9c5e44769cd57
- https://git.kernel.org/stable/c/a698ac8ab2561cf575d2d9f34095032651dd952e
- https://git.kernel.org/stable/c/e196115ec330a18de415bdb9f5071aa9f08e53ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52912.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52912
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
