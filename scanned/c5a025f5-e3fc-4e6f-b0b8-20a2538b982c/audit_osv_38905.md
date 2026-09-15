# [C] ip6_tunnel: clear skb2->cb[] in ip4ip6_err()

## Summary
Severity: Critical
Advisory: CVE-2026-43037
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43037
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip6_tunnel: clear skb2->cb[] in ip4ip6_err()

Oskar Kjos reported the following problem.

ip4ip6_err() calls icmp_send() on a cloned skb whose cb[] was written
by the IPv6 receive path as struct inet6_skb_parm. icmp_send() passes
IPCB(skb2) to __ip_options_echo(), which interprets that cb[] region
as struct inet_skb_parm (IPv4). The layouts differ: inet6_skb_parm.nhoff
at offset 14 overlaps inet_skb_parm.opt.rr, producing a non-zero rr
value. __ip_options_echo() then reads optlen from attacker-controlled
packet data at sptr[rr+1] and copies that many bytes into dopt->__data,
a fixed 40-byte stack buffer (IP_OPTIONS_DATA_FIXED_SIZE).

To fix this we clear skb2->cb[], as suggested by Oskar Kjos.

Also add minimal IPv4 header validation (version == 4, ihl >= 5).

## References
- https://git.kernel.org/stable/c/1063515ce15ff31065c4e7f8265f4c2fd3c54876
- https://git.kernel.org/stable/c/2cc6e3b0fe0f0242d1f530a93a4924f48ab85ba5
- https://git.kernel.org/stable/c/2edfa31769a4add828a7e604b21cb82aaaa05925
- https://git.kernel.org/stable/c/4a622658f384b03560834cbe8ffcfe69a278f7c8
- https://git.kernel.org/stable/c/590f622669b97eaf7b57a1de7b0a6e68c5d8b2c3
- https://git.kernel.org/stable/c/a0c4ce9900a108eaf55d0f3b399cb55999647d39
- https://git.kernel.org/stable/c/d6621f60192fe10c047a4487be42a6f4c150707f
- https://git.kernel.org/stable/c/ea9f65b27c8404e164848ebff1443310fd187629
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43037.json
- https://access.redhat.com/errata/RHSA-2026:22900
- https://access.redhat.com/errata/RHSA-2026:22940
- https://access.redhat.com/errata/RHSA-2026:22964
- https://access.redhat.com/errata/RHSA-2026:23224
- https://access.redhat.com/errata/RHSA-2026:23237
- https://access.redhat.com/errata/RHSA-2026:24343
- https://access.redhat.com/errata/RHSA-2026:25044
- https://access.redhat.com/errata/RHSA-2026:25120
- https://access.redhat.com/errata/RHSA-2026:25121
- https://access.redhat.com/errata/RHSA-2026:25181
- https://access.redhat.com/errata/RHSA-2026:25186
