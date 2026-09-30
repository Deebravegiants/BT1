# [H] macsec: fix UAF bug for real_dev

## Summary
Severity: High
Advisory: CVE-2022-49390
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49390
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.17.15, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

macsec: fix UAF bug for real_dev

Create a new macsec device but not get reference to real_dev. That can
not ensure that real_dev is freed after macsec. That will trigger the
UAF bug for real_dev as following:

==================================================================
BUG: KASAN: use-after-free in macsec_get_iflink+0x5f/0x70 drivers/net/macsec.c:3662
Call Trace:
 ...
 macsec_get_iflink+0x5f/0x70 drivers/net/macsec.c:3662
 dev_get_iflink+0x73/0xe0 net/core/dev.c:637
 default_operstate net/core/link_watch.c:42 [inline]
 rfc2863_policy+0x233/0x2d0 net/core/link_watch.c:54
 linkwatch_do_dev+0x2a/0x150 net/core/link_watch.c:161

Allocated by task 22209:
 ...
 alloc_netdev_mqs+0x98/0x1100 net/core/dev.c:10549
 rtnl_create_link+0x9d7/0xc00 net/core/rtnetlink.c:3235
 veth_newlink+0x20e/0xa90 drivers/net/veth.c:1748

Freed by task 8:
 ...
 kfree+0xd6/0x4d0 mm/slub.c:4552
 kvfree+0x42/0x50 mm/util.c:615
 device_release+0x9f/0x240 drivers/base/core.c:2229
 kobject_cleanup lib/kobject.c:673 [inline]
 kobject_release lib/kobject.c:704 [inline]
 kref_put include/linux/kref.h:65 [inline]
 kobject_put+0x1c8/0x540 lib/kobject.c:721
 netdev_run_todo+0x72e/0x10b0 net/core/dev.c:10327

After commit faab39f63c1f ("net: allow out-of-order netdev unregistration")
and commit e5f80fcf869a ("ipv6: give an IPv6 dev to blackhole_netdev"), we
can add dev_hold_track() in macsec_dev_init() and dev_put_track() in
macsec_free_netdev() to fix the problem.

## References
- https://git.kernel.org/stable/c/196a888ca6571deb344468e1d7138e3273206335
- https://git.kernel.org/stable/c/78933cbc143b82d02330e00900d2fd08f2682f4e
- https://git.kernel.org/stable/c/d130282179aa6051449ac8f8df1115769998a665
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49390.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
