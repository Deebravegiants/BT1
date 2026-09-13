# [H] nexthop: avoid unlocked f6i_list walk in nh_rt_cache_flush

## Summary
Severity: High
Advisory: CVE-2026-74561
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74561
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nexthop: avoid unlocked f6i_list walk in nh_rt_cache_flush

nh_rt_cache_flush() walks nh->f6i_list during an RTNL-serialized nexthop
replace without holding nh->lock, racing the unlocked IPv6 route
add/delete that mutate the list under nh->lock and free fib6_info
entries (nh_rt_cache_flush() is inlined into rtm_new_nexthop()):

  BUG: KASAN: slab-use-after-free in nh_rt_cache_flush (net/ipv4/nexthop.c:2243)
  Read of size 8 at addr ffff888012953e18 by task exploit/146
   nh_rt_cache_flush (net/ipv4/nexthop.c:2243)
   replace_nexthop (net/ipv4/nexthop.c:2610)
   rtm_new_nexthop (net/ipv4/nexthop.c:3323)
   rtnetlink_rcv_msg (net/core/rtnetlink.c:7076)

Unlike the other f6i_list walks, this one bumps each route's sernum via
fib6_update_sernum_upto_root(), which needs tb6_lock; taking nh->lock
around it would invert the established tb6_lock -> nh->lock order and
deadlock. As the only purpose is to invalidate cached dsts, bump the
IPv6 sernum for the whole netns with rt_genid_bump_ipv6() instead,
mirroring the rt_cache_flush() already done for IPv4 just above.

## References
- https://git.kernel.org/stable/c/44f53e4331a30fabc38a411fae7524341b618db3
- https://git.kernel.org/stable/c/4787a6d2629b4e8c0b6bacab1f75c1660eca44d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74561.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74561
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
