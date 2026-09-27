# [M] net: Fix icmp host relookup triggering ip_rt_bug

## Summary
Severity: Medium
Advisory: CVE-2024-56647
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56647
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: Fix icmp host relookup triggering ip_rt_bug

arp link failure may trigger ip_rt_bug while xfrm enabled, call trace is:

WARNING: CPU: 0 PID: 0 at net/ipv4/route.c:1241 ip_rt_bug+0x14/0x20
Modules linked in:
CPU: 0 UID: 0 PID: 0 Comm: swapper/0 Not tainted 6.12.0-rc6-00077-g2e1b3cc9d7f7
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
BIOS rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org 04/01/2014
RIP: 0010:ip_rt_bug+0x14/0x20
Call Trace:
 <IRQ>
 ip_send_skb+0x14/0x40
 __icmp_send+0x42d/0x6a0
 ipv4_link_failure+0xe2/0x1d0
 arp_error_report+0x3c/0x50
 neigh_invalidate+0x8d/0x100
 neigh_timer_handler+0x2e1/0x330
 call_timer_fn+0x21/0x120
 __run_timer_base.part.0+0x1c9/0x270
 run_timer_softirq+0x4c/0x80
 handle_softirqs+0xac/0x280
 irq_exit_rcu+0x62/0x80
 sysvec_apic_timer_interrupt+0x77/0x90

The script below reproduces this scenario:
ip xfrm policy add src 0.0.0.0/0 dst 0.0.0.0/0 \
	dir out priority 0 ptype main flag localok icmp
ip l a veth1 type veth
ip a a 192.168.141.111/24 dev veth0
ip l s veth0 up
ping 192.168.141.155 -c 1

icmp_route_lookup() create input routes for locally generated packets
while xfrm relookup ICMP traffic.Then it will set input route
(dst->out = ip_rt_bug) to skb for DESTUNREACH.

For ICMP err triggered by locally generated packets, dst->dev of output
route is loopback. Generally, xfrm relookup verification is not required
on loopback interfaces (net.ipv4.conf.lo.disable_xfrm = 1).

Skip icmp relookup for locally generated packets to fix it.

## References
- https://git.kernel.org/stable/c/9545011e7b2a8fc0cbd6e387a09f12cd41d7d82f
- https://git.kernel.org/stable/c/c44daa7e3c73229f7ac74985acb8c7fb909c4e0a
- https://git.kernel.org/stable/c/d50981aaaefc3b04490fbc8274d37881a2b1b112
- https://git.kernel.org/stable/c/da54b3039d436227deebbc202cefea63bd318a38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56647.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56647
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
