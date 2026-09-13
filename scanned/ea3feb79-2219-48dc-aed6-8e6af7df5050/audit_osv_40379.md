# [H] sctp: disable BH before calling udp_tunnel_xmit_skb()

## Summary
Severity: High
Advisory: CVE-2026-53070
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53070
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: disable BH before calling udp_tunnel_xmit_skb()

udp_tunnel_xmit_skb() / udp_tunnel6_xmit_skb() are expected to run with
BH disabled.  After commit 6f1a9140ecda ("add xmit recursion limit to
tunnel xmit functions"), on the path:

  udp(6)_tunnel_xmit_skb() -> ip(6)tunnel_xmit()

dev_xmit_recursion_inc()/dec() must stay balanced on the same CPU.

Without local_bh_disable(), the context may move between CPUs, which can
break the inc/dec pairing. This may lead to incorrect recursion level
detection and cause packets to be dropped in ip(6)_tunnel_xmit() or
__dev_queue_xmit().

Fix it by disabling BH around both IPv4 and IPv6 SCTP UDP xmit paths.

In my testing, after enabling the SCTP over UDP:

  # ip net exec ha sysctl -w net.sctp.udp_port=9899
  # ip net exec ha sysctl -w net.sctp.encap_port=9899
  # ip net exec hb sysctl -w net.sctp.udp_port=9899
  # ip net exec hb sysctl -w net.sctp.encap_port=9899

  # ip net exec ha iperf3 -s

- without this patch:

  # ip net exec hb iperf3 -c 192.168.0.1 --sctp
  [  5]   0.00-10.00  sec  37.2 MBytes  31.2 Mbits/sec  sender
  [  5]   0.00-10.00  sec  37.1 MBytes  31.1 Mbits/sec  receiver

- with this patch:

  # ip net exec hb iperf3 -c 192.168.0.1 --sctp
  [  5]   0.00-10.00  sec  3.14 GBytes  2.69 Gbits/sec  sender
  [  5]   0.00-10.00  sec  3.14 GBytes  2.69 Gbits/sec  receiver

## References
- https://git.kernel.org/stable/c/0de7db2eb27e82b983157016fa604b1ba664ae5f
- https://git.kernel.org/stable/c/2cd7e6971fc2787408ceef17906ea152791448cf
- https://git.kernel.org/stable/c/790093245e35040c2adb15f48970020425aa3f47
- https://git.kernel.org/stable/c/be3bfcb34bda04f6a350710db471d4133f950f2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53070.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
