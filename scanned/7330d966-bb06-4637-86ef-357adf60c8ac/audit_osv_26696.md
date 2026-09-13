# [C] tunnels: fix kasan splat when generating ipv4 pmtu error

## Summary
Severity: Critical
Advisory: CVE-2023-53600
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53600
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.191, >=5.11.0 <5.15.127, >=5.16.0 <6.1.46, >=6.2.0 <6.4.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

tunnels: fix kasan splat when generating ipv4 pmtu error

If we try to emit an icmp error in response to a nonliner skb, we get

BUG: KASAN: slab-out-of-bounds in ip_compute_csum+0x134/0x220
Read of size 4 at addr ffff88811c50db00 by task iperf3/1691
CPU: 2 PID: 1691 Comm: iperf3 Not tainted 6.5.0-rc3+ #309
[..]
 kasan_report+0x105/0x140
 ip_compute_csum+0x134/0x220
 iptunnel_pmtud_build_icmp+0x554/0x1020
 skb_tunnel_check_pmtu+0x513/0xb80
 vxlan_xmit_one+0x139e/0x2ef0
 vxlan_xmit+0x1867/0x2760
 dev_hard_start_xmit+0x1ee/0x4f0
 br_dev_queue_push_xmit+0x4d1/0x660
 [..]

ip_compute_csum() cannot deal with nonlinear skbs, so avoid it.
After this change, splat is gone and iperf3 is no longer stuck.

## References
- https://git.kernel.org/stable/c/5850c391fd7e25662334cb3cbf29a62bcbff1084
- https://git.kernel.org/stable/c/6a7ac3d20593865209dceb554d8b3f094c6bd940
- https://git.kernel.org/stable/c/da5f42a6e7485fbb7a6dbd6a2b3045e19e4df5cc
- https://git.kernel.org/stable/c/e95808121953410db8c59f0abfde70ac0d34222c
- https://git.kernel.org/stable/c/fe6a9f7516735be9fdabab00e47ef7a3403a174d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53600.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53600
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
