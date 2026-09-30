# [C] ipv6: fix possible UAF in icmpv6_rcv()

## Summary
Severity: Critical
Advisory: CVE-2026-53006
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53006
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix possible UAF in icmpv6_rcv()

Caching saddr and daddr before pskb_pull() is problematic
since skb->head can change.

Remove these temporary variables:

- We only access &ipv6_hdr(skb)->saddr and &ipv6_hdr(skb)->daddr
  when net_dbg_ratelimited() is called in the slow path.

- Avoid potential future misuse after pskb_pull() call.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0069813e6ca9309eca78022bcb3aeb1e9ef90a12
- https://git.kernel.org/stable/c/085e31a811ef234ef8c3e219c4636dfebfe7e10f
- https://git.kernel.org/stable/c/1e1f0f89ee4692a64be3f3707ff8ac1ae57b03e7
- https://git.kernel.org/stable/c/38bdbc897c0d83a3e2b925a51b69420f1feba29a
- https://git.kernel.org/stable/c/7bff2c8fe5c35ae58bf73104f53db3676e6e5d94
- https://git.kernel.org/stable/c/7c66b368c6ff453f99cb39d84af93e908e51eef2
- https://git.kernel.org/stable/c/aff0f28f5be803de2452ce702631c021fcd9ce8a
- https://git.kernel.org/stable/c/f996edd7615e686ada141b7f3395025729ff8ccb
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53006.json
- https://access.redhat.com/errata/RHSA-2026:45192
- https://access.redhat.com/errata/RHSA-2026:47010
- https://access.redhat.com/errata/RHSA-2026:47011
- https://access.redhat.com/errata/RHSA-2026:47017
- https://access.redhat.com/errata/RHSA-2026:61932
- https://access.redhat.com/errata/RHSA-2026:62568
- https://access.redhat.com/errata/RHSA-2026:64767
- https://access.redhat.com/errata/RHSA-2026:65710
- https://access.redhat.com/errata/RHSA-2026:65711
- https://access.redhat.com/errata/RHSA-2026:65712
