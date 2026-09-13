# [H] vxlan: do not arm the ageing timer on a device that is down

## Summary
Severity: High
Advisory: CVE-2026-74615
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74615
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: do not arm the ageing timer on a device that is down

vxlan_changelink() arms vxlan->age_timer whenever the requested ageing
interval differs from the configured one:

	if (conf.age_interval != vxlan->cfg.age_interval)
		mod_timer(&vxlan->age_timer, jiffies);

There is no netif_running() test, so the timer is armed even on a device
that was never brought up.  The only synchronous cancel in the driver is
the timer_delete_sync() in vxlan_stop(), which is .ndo_stop.
netif_close_many() drops devices without IFF_UP before
__dev_close_many() runs, so that cancel is skipped for such a device.

vxlan_setup() sets dev->needs_free_netdev = true and age_timer is a
member of struct vxlan_dev, so free_netdev() releases the allocation the
timer lives in while it is still queued on a timer_base.
expire_timers() unlinks the entry before it loads timer->function, so
the timer core writes through the freed object's list pointers:

  BUG: KASAN: slab-use-after-free in __run_timers+0x208/0x654
  Write of size 8 at addr ffff00001adace68 by task true/192
   __asan_store8+0x84/0xac
   __run_timers+0x208/0x654
   run_timer_softirq+0x154/0x18c
  Allocated by task 189:
   alloc_netdev_mqs+0x64/0x720
   rtnl_create_link+0x4ac/0x520
   rtnl_newlink+0x758/0xd00
  Freed by task 191:
   netdev_release+0x40/0x58
   netdev_run_todo+0x4a4/0x8c0
   rtnl_dellink+0x200/0x4e8

The rtnl operations involved are netns-scoped, so an unprivileged user
can perform them in a new user and network namespace.

Arming the timer on a down device never had an effect: vxlan_cleanup()
returns early on !netif_running(), and vxlan_open() arms the timer for
any non-zero interval once the device is brought up.  Add the missing
test.

Discovered by XBOW, triaged by Baul Lee <baul.lee@xbow.com>

## References
- https://git.kernel.org/stable/c/26c179d47403d2f919ee914cc02c31d896b59fee
- https://git.kernel.org/stable/c/46bb297ad77680e009244f067f27d51cf5b8c7cf
- https://git.kernel.org/stable/c/619dd29045e439d0b0f8c6d4fec1af447a050680
- https://git.kernel.org/stable/c/6b095e99b9e67ea31f0c4b00260e010898253519
- https://git.kernel.org/stable/c/6b4119af544996a545cf84b16f1dbce829ba0de8
- https://git.kernel.org/stable/c/9dc561f0522c35bdd66e0646a748814a138ec4ca
- https://git.kernel.org/stable/c/b37971686ec59fb027fa4910ba16805e68fddb97
- https://git.kernel.org/stable/c/be44d79d14d7f9ae7c8ffb7272142005341b5123
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74615.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74615
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
