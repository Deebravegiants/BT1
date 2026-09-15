# [H] xfrm6: clear dst.dev on error to avoid double netdev_put in xfrm6_fill_dst()

## Summary
Severity: High
Advisory: CVE-2026-64580
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64580
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm6: clear dst.dev on error to avoid double netdev_put in xfrm6_fill_dst()

On the error path where in6_dev_get(dev) returns NULL, xfrm6_fill_dst()
releases the device reference with netdev_put() but leaves
xdst->u.dst.dev set. dst_destroy() later calls netdev_put(dst->dev)
again, so the same net_device reference is released twice, underflowing
its refcount (ref_tracker WARNING + "unregister_netdevice: waiting for
<dev> to become free").

Clear xdst->u.dst.dev after the netdev_put(), the same way the XFRM
device-offload paths xfrm_dev_state_add() and xfrm_dev_policy_add() in
net/xfrm/xfrm_device.c NULL ->dev when releasing the reference on error.

  ref_tracker: reference already released.
  ref_tracker: allocated in:
   xfrm6_fill_dst (net/ipv6/xfrm6_policy.c:86)
   ...
   udpv6_sendmsg (net/ipv6/udp.c:1696)
   ...
  ref_tracker: freed in:
   xfrm6_fill_dst (net/ipv6/xfrm6_policy.c:90)
   ...
  WARNING: lib/ref_tracker.c:322 at ref_tracker_free+0x58b/0x780
   dst_destroy (net/core/dst.c:115)
   rcu_core
   handle_softirqs
   ...

## References
- https://git.kernel.org/stable/c/136992de9bb91871084ae52d172610541c76e4d2
- https://git.kernel.org/stable/c/43de8a49335e611adb271bbd52e84dfbc11fc185
- https://git.kernel.org/stable/c/97e032e5733e49471fb73de117ea2ac1ac7c479a
- https://git.kernel.org/stable/c/df6856c2dda9187601d29b5fbd7a81b3b178cedf
- https://git.kernel.org/stable/c/e078da1b4e11390cff3201c19a9a1fe70c5b934f
- https://git.kernel.org/stable/c/ff636d7b7cba6dea82ecf580415ea57f2c1a11b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64580.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
