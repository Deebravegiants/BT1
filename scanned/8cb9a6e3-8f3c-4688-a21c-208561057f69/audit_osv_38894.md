# [C] net/x25: Fix potential double free of skb

## Summary
Severity: Critical
Advisory: CVE-2026-43011
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43011
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/x25: Fix potential double free of skb

When alloc_skb fails in x25_queue_rx_frame it calls kfree_skb(skb) at
line 48 and returns 1 (error).
This error propagates back through the call chain:

x25_queue_rx_frame returns 1
    |
    v
x25_state3_machine receives the return value 1 and takes the else
branch at line 278, setting queued=0 and returning 0
    |
    v
x25_process_rx_frame returns queued=0
    |
    v
x25_backlog_rcv at line 452 sees queued=0 and calls kfree_skb(skb)
again

This would free the same skb twice. Looking at x25_backlog_rcv:

net/x25/x25_in.c:x25_backlog_rcv() {
    ...
    queued = x25_process_rx_frame(sk, skb);
    ...
    if (!queued)
        kfree_skb(skb);
}

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/143d4fa68ae9efb83b0c55b12cc7f0d03732a2b1
- https://git.kernel.org/stable/c/3f5e3005984645bf5bd129c6b13149879580b1fb
- https://git.kernel.org/stable/c/524371398d8463ea7e101fce2cbf3915645d1730
- https://git.kernel.org/stable/c/5d0aa038a90b30c9bedde0c41c1fdcd98ecb16e9
- https://git.kernel.org/stable/c/c87dd137c0dad07cc55f98181ff380b0c23d2878
- https://git.kernel.org/stable/c/d10a26aa4d072320530e6968ef945c8c575edf61
- https://git.kernel.org/stable/c/f782dd382203b2a8c4552a628431b7de65a19a7b
- https://git.kernel.org/stable/c/fa1dbc93530b34fab0da9862426fe9c918c74dc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43011.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
