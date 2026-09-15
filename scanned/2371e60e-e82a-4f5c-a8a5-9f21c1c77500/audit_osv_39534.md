# [H] net: ipv6: fix NOREF dst use in seg6 and rpl lwtunnels

## Summary
Severity: High
Advisory: CVE-2026-46099
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46099
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ipv6: fix NOREF dst use in seg6 and rpl lwtunnels

seg6_input_core() and rpl_input() call ip6_route_input() which sets a
NOREF dst on the skb, then pass it to dst_cache_set_ip6() invoking
dst_hold() unconditionally.
On PREEMPT_RT, ksoftirqd is preemptible and a higher-priority task can
release the underlying pcpu_rt between the lookup and the caching
through a concurrent FIB lookup on a shared nexthop.
Simplified race sequence:

  ksoftirqd/X                       higher-prio task (same CPU X)
  -----------                       --------------------------------
  seg6_input_core(,skb)/rpl_input(skb)
    dst_cache_get()
      -> miss
    ip6_route_input(skb)
      -> ip6_pol_route(,skb,flags)
         [RT6_LOOKUP_F_DST_NOREF in flags]
        -> FIB lookup resolves fib6_nh
           [nhid=N route]
        -> rt6_make_pcpu_route()
           [creates pcpu_rt, refcount=1]
             pcpu_rt->sernum = fib6_sernum
             [fib6_sernum=W]
           -> cmpxchg(fib6_nh.rt6i_pcpu,
                      NULL, pcpu_rt)
              [slot was empty, store succeeds]
      -> skb_dst_set_noref(skb, dst)
         [dst is pcpu_rt, refcount still 1]

                                    rt_genid_bump_ipv6()
                                      -> bumps fib6_sernum
                                         [fib6_sernum from W to Z]
                                    ip6_route_output()
                                      -> ip6_pol_route()
                                        -> FIB lookup resolves fib6_nh
                                           [nhid=N]
                                        -> rt6_get_pcpu_route()
                                             pcpu_rt->sernum != fib6_sernum
                                             [W <> Z, stale]
                                          -> prev = xchg(rt6i_pcpu, NULL)
                                          -> dst_release(prev)
                                             [prev is pcpu_rt,
                                              refcount 1->0, dead]

    dst = skb_dst(skb)
    [dst is the dead pcpu_rt]
    dst_cache_set_ip6(dst)
      -> dst_hold() on dead dst
      -> WARN / use-after-free

For the race to occur, ksoftirqd must be preemptible (PREEMPT_RT without
PREEMPT_RT_NEEDS_BH_LOCK) and a concurrent task must be able to release
the pcpu_rt. Shared nexthop objects provide such a path, as two routes
pointing to the same nhid share the same fib6_nh and its rt6i_pcpu
entry.

Fix seg6_input_core() and rpl_input() by calling skb_dst_force() after
ip6_route_input() to force the NOREF dst into a refcounted one before
caching.
The output path is not affected as ip6_route_output() already returns a
refcounted dst.

## References
- https://git.kernel.org/stable/c/51fef5a7c4d160839199e941929456ba21ddf73c
- https://git.kernel.org/stable/c/52f9db67f8f35f436366cf4980b4f0a2583d0ef0
- https://git.kernel.org/stable/c/6bd17925bd6866027a6555db17905b9fc073d38d
- https://git.kernel.org/stable/c/9dd5481f960e337b81d7dfe429529495c1c481c0
- https://git.kernel.org/stable/c/b258b849a580285a1692e782ebc902b44c884a71
- https://git.kernel.org/stable/c/b778b6d095421619c331fd2d7751143cd5387103
- https://git.kernel.org/stable/c/f9c52a6ba9780bd27e0bf4c044fd91c13c778b6e
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46099.json
- https://access.redhat.com/errata/RHSA-2026:45114
- https://access.redhat.com/errata/RHSA-2026:59662
- https://access.redhat.com/errata/RHSA-2026:59663
- https://access.redhat.com/errata/RHSA-2026:62568
- https://access.redhat.com/errata/RHSA-2026:64767
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-46099
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46099
- https://bugzilla.redhat.com/show_bug.cgi?id=2481972
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
