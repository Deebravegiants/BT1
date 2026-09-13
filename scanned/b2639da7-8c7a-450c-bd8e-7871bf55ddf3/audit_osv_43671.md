# [H] nexthop: take nh->lock for f6i_list walks in replace check and notify

## Summary
Severity: High
Advisory: CVE-2026-74562
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74562
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nexthop: take nh->lock for f6i_list walks in replace check and notify

fib6_check_nh_list() and __nexthop_replace_notify() walk nh->f6i_list
during an RTNL-serialized nexthop replace without holding nh->lock. IPv6
RTM_NEWROUTE/RTM_DELROUTE run without RTNL and mutate that list under
nh->lock (fib6_add_rt2node_nh(), fib6_purge_rt()), so both walks race a
concurrent route delete that unlinks and frees a fib6_info:

  BUG: KASAN: slab-use-after-free in rt6_fill_node.isra.0 (net/ipv6/route.c:5799)
  Read of size 4 at addr ffff888014607e64 by task exploit/143
   rt6_fill_node.isra.0 (net/ipv6/route.c:5799)
   fib6_rt_update (net/ipv6/route.c:6412)
   __nexthop_replace_notify (net/ipv4/nexthop.c:2542)
   rtm_new_nexthop (net/ipv4/nexthop.c:2554)
   rtnetlink_rcv_msg (net/core/rtnetlink.c:7076)

  BUG: KASAN: slab-use-after-free in fib6_check_nh_list (net/ipv4/nexthop.c:1605)
  Read of size 8 at addr ffff888014a7d068 by task exploit/142
   fib6_check_nh_list (net/ipv4/nexthop.c:1605)
   rtm_new_nexthop (net/ipv4/nexthop.c:2575)
   rtnetlink_rcv_msg (net/core/rtnetlink.c:7076)

Both walks only read the entries and take no tb6_lock, so protect them
with nh->lock; fib6_rt_update() uses gfp_any(), which returns GFP_ATOMIC
under the lock.

## References
- https://git.kernel.org/stable/c/072cd1f21819dedd2252e704d255de3b0cfc61a7
- https://git.kernel.org/stable/c/bb2b072c619c1f741a6234257050f72005dc63ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74562.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74562
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
