# [H] ipv6: reject malicious packets in ipv6_gso_segment()

## Summary
Severity: High
Advisory: CVE-2025-38572
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38572
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: reject malicious packets in ipv6_gso_segment()

syzbot was able to craft a packet with very long IPv6 extension headers
leading to an overflow of skb->transport_header.

This 16bit field has a limited range.

Add skb_reset_transport_header_careful() helper and use it
from ipv6_gso_segment()

WARNING: CPU: 0 PID: 5871 at ./include/linux/skbuff.h:3032 skb_reset_transport_header include/linux/skbuff.h:3032 [inline]
WARNING: CPU: 0 PID: 5871 at ./include/linux/skbuff.h:3032 ipv6_gso_segment+0x15e2/0x21e0 net/ipv6/ip6_offload.c:151
Modules linked in:
CPU: 0 UID: 0 PID: 5871 Comm: syz-executor211 Not tainted 6.16.0-rc6-syzkaller-g7abc678e3084 #0 PREEMPT(full)
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 07/12/2025
 RIP: 0010:skb_reset_transport_header include/linux/skbuff.h:3032 [inline]
 RIP: 0010:ipv6_gso_segment+0x15e2/0x21e0 net/ipv6/ip6_offload.c:151
Call Trace:
 <TASK>
  skb_mac_gso_segment+0x31c/0x640 net/core/gso.c:53
  nsh_gso_segment+0x54a/0xe10 net/nsh/nsh.c:110
  skb_mac_gso_segment+0x31c/0x640 net/core/gso.c:53
  __skb_gso_segment+0x342/0x510 net/core/gso.c:124
  skb_gso_segment include/net/gso.h:83 [inline]
  validate_xmit_skb+0x857/0x11b0 net/core/dev.c:3950
  validate_xmit_skb_list+0x84/0x120 net/core/dev.c:4000
  sch_direct_xmit+0xd3/0x4b0 net/sched/sch_generic.c:329
  __dev_xmit_skb net/core/dev.c:4102 [inline]
  __dev_queue_xmit+0x17b6/0x3a70 net/core/dev.c:4679

## References
- https://git.kernel.org/stable/c/09ff062b89d8e48165247d677d1ca23d6d607e9b
- https://git.kernel.org/stable/c/3f638e0b28bde7c3354a0df938ab3a96739455d1
- https://git.kernel.org/stable/c/5489e7fc6f8be3062f8cb7e49406de4bfd94db67
- https://git.kernel.org/stable/c/573b8250fc2554761db3bc2bbdbab23789d52d4e
- https://git.kernel.org/stable/c/5dc60b2a00ed7629214ac0c48e43f40af2078703
- https://git.kernel.org/stable/c/d45cf1e7d7180256e17c9ce88e32e8061a7887fe
- https://git.kernel.org/stable/c/de322cdf600fc9433845a9e944d1ca6b31cfb67e
- https://git.kernel.org/stable/c/ee851768e4b8371ce151fd446d24bf3ae2d18789
- https://git.kernel.org/stable/c/ef05007b403dcc21e701cb1f30d4572ac0a9da20
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38572.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38572
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
