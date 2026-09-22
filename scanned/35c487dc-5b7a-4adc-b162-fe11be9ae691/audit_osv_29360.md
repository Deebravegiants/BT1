# [C] net: rswitch: Avoid use-after-free in rswitch_poll()

## Summary
Severity: Critical
Advisory: CVE-2024-42108
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42108
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rswitch: Avoid use-after-free in rswitch_poll()

The use-after-free is actually in rswitch_tx_free(), which is inlined in
rswitch_poll(). Since `skb` and `gq->skbs[gq->dirty]` are in fact the
same pointer, the skb is first freed using dev_kfree_skb_any(), then the
value in skb->len is used to update the interface statistics.

Let's move around the instructions to use skb->len before the skb is
freed.

This bug is trivial to reproduce using KFENCE. It will trigger a splat
every few packets. A simple ARP request or ICMP echo request is enough.

## References
- https://git.kernel.org/stable/c/4a41bb9f2b402469d425a1c13359d3b3ea4e6403
- https://git.kernel.org/stable/c/92cbbe7759193e3418f38d0d73f8fe125312c58b
- https://git.kernel.org/stable/c/9a0c28efeec6383ef22e97437616b920e7320b67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42108.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
