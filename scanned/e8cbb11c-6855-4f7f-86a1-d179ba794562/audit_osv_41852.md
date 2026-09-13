# [C] vxlan: do not reuse cached ip_hdr() value after skb_tunnel_check_pmtu()

## Summary
Severity: Critical
Advisory: CVE-2026-63993
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63993
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: do not reuse cached ip_hdr() value after skb_tunnel_check_pmtu()

skb_tunnel_check_pmtu() can change skb->head.

Reusing old_iph afer skb_tunnel_check_pmtu() can cause an UAF.

Use instead ip_hdr(skb) as done in drivers/net/bareudp.c
and drivers/net/geneve.c.

Found by Sashiko.

## References
- https://git.kernel.org/stable/c/5303925e360527243b46a440a04667826bbc72b7
- https://git.kernel.org/stable/c/609e63312c29aad18026a1d3222e123d4b6b0feb
- https://git.kernel.org/stable/c/6b8bfce9d2f774d2c2243e0248e03efb99bba6c0
- https://git.kernel.org/stable/c/7d9ef0cb271555d8cf39fefe6c981e1493b25ecf
- https://git.kernel.org/stable/c/8d435d68d71fb875876b722f4136caf74f2f48bd
- https://git.kernel.org/stable/c/9257f56ac47ef1976bcd056cf986a9988eeec67a
- https://git.kernel.org/stable/c/a493efd4336cf19122ae0e4cbb3d31b32d70deea
- https://git.kernel.org/stable/c/dc3bfa050f873371e745bdf478b1f5b738e5733d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63993.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63993
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
