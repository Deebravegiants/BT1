# [C] ipv6: icmp: clear skb2->cb[] in ip6_err_gen_icmpv6_unreach()

## Summary
Severity: Critical
Advisory: CVE-2026-43038
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43038
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: icmp: clear skb2->cb[] in ip6_err_gen_icmpv6_unreach()

Sashiko AI-review observed:

  In ip6_err_gen_icmpv6_unreach(), the skb is an outer IPv4 ICMP error packet
  where its cb contains an IPv4 inet_skb_parm. When skb is cloned into skb2
  and passed to icmp6_send(), it uses IP6CB(skb2).

  IP6CB interprets the IPv4 inet_skb_parm as an inet6_skb_parm. The cipso
  offset in inet_skb_parm.opt directly overlaps with dsthao in inet6_skb_parm
  at offset 18.

  If an attacker sends a forged ICMPv4 error with a CIPSO IP option, dsthao
  would be a non-zero offset. Inside icmp6_send(), mip6_addr_swap() is called
  and uses ipv6_find_tlv(skb, opt->dsthao, IPV6_TLV_HAO).

  This would scan the inner, attacker-controlled IPv6 packet starting at that
  offset, potentially returning a fake TLV without checking if the remaining
  packet length can hold the full 18-byte struct ipv6_destopt_hao.

  Could mip6_addr_swap() then perform a 16-byte swap that extends past the end
  of the packet data into skb_shared_info?

  Should the cb array also be cleared in ip6_err_gen_icmpv6_unreach() and
  ip6ip6_err() to prevent this?

This patch implements the first suggestion.

I am not sure if ip6ip6_err() needs to be changed.
A separate patch would be better anyway.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0452b6526b2f54b2413b9cb4ff1ea2ac542c99c7
- https://git.kernel.org/stable/c/1ceeebd5bd6d855b17a5df625109bfe29129d7cf
- https://git.kernel.org/stable/c/3d5127d998de617b130aae96b138dba22ac6a8a7
- https://git.kernel.org/stable/c/86ab3e55673a7a49a841838776f1ab18d23a67b5
- https://git.kernel.org/stable/c/a2edbb6393972a02114b6003953a5cef3104fada
- https://git.kernel.org/stable/c/a4437faf135da293d16fcc4cc607316742bd0ebb
- https://git.kernel.org/stable/c/c438ba010171b70bad22fc18b1d5bdc3627476e8
- https://git.kernel.org/stable/c/e41953e7d118e2702bcb217879c173d9d1d3cd4e
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43038.json
- https://access.redhat.com/errata/RHSA-2026:22900
- https://access.redhat.com/errata/RHSA-2026:22940
- https://access.redhat.com/errata/RHSA-2026:22964
- https://access.redhat.com/errata/RHSA-2026:23224
- https://access.redhat.com/errata/RHSA-2026:23237
- https://access.redhat.com/errata/RHSA-2026:24343
- https://access.redhat.com/errata/RHSA-2026:25120
- https://access.redhat.com/errata/RHSA-2026:25121
- https://access.redhat.com/errata/RHSA-2026:25533
