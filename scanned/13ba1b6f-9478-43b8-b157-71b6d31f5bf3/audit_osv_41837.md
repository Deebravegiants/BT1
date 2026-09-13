# [H] ipv6: fix possible infinite loop in fib6_select_path()

## Summary
Severity: High
Advisory: CVE-2026-63968
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63968
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix possible infinite loop in fib6_select_path()

Found while auditing the same pattern Sashiko reported in
rt6_fill_node() [1]. Apply the same fix as
commit f8d8ce1b515a ("ipv6: fix possible infinite loop in fib6_info_uses_dev()").

Writers holding tb6_lock can list_del_rcu(&first->fib6_siblings)
without waiting for RCU readers; first->fib6_siblings.next then
still points into the old ring and this softirq-side walker never
reaches &first->fib6_siblings as its terminator. fib6_purge_rt()
always WRITE_ONCE()s first->fib6_nsiblings to 0 before
list_del_rcu(), so an inside-loop check is a reliable detach signal.

[1] https://sashiko.dev/#/patchset/20260526020227.4857-1-jiayuan.chen%40linux.dev

## References
- https://git.kernel.org/stable/c/0f7b73c3452635de83b8711b31abdda8e49aad7b
- https://git.kernel.org/stable/c/3948a7d92f7678e89e1776bb2d169afcad63b1ae
- https://git.kernel.org/stable/c/9b9d5bd6e3d4c9cecab5407604b690684b2532d2
- https://git.kernel.org/stable/c/9c7da87c2dc860bb17ca1ece942495d28b1ce3b9
- https://git.kernel.org/stable/c/ab9a10969a907b472a0196d999c08ff7144172e3
- https://git.kernel.org/stable/c/c87cd3cb309634bc8f50a54e2079424f219ac21f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63968.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
