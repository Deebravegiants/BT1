# [H] net: openvswitch: fix potential UAF on meter attach failure

## Summary
Severity: High
Advisory: CVE-2026-74465
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74465
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: fix potential UAF on meter attach failure

While attaching a newly created meter attach_meter() function makes
the new meter visible to other CPUs but can still fail afterwards.
On failure, it detaches the meter back and returns an error.

However, this is an unexpected behavior for the ovs_meter_cmd_set()
that uses a plain kfree(meter) on attach failure without waiting for
RCU readers to stop using it, assuming it was never visible.

This is never a problem for ovs-vswitchd as it always creates meters
before creating any flows that use them.  But the UAF can be triggered
with a custom application using uAPI:

 BUG: KASAN: slab-use-after-free in ovs_meter_execute (net/openvswitch/meter.c:653)
 Read of size 8 at addr ffff88810d152650 by task meter/2508

 Call Trace:
  ovs_meter_execute (net/openvswitch/meter.c:653)
  do_execute_actions (net/openvswitch/actions.c:1407)
  ovs_execute_actions (net/openvswitch/actions.c:1584)
  ovs_packet_cmd_execute (net/openvswitch/datapath.c:703)
  ...
  netlink_sendmsg (af_netlink.c:1900)

 Allocated by task 2519:
  __kasan_kmalloc (mm/kasan/common.c:398 mm/kasan/common.c:415)
  ovs_meter_cmd_set (net/openvswitch/meter.c:422)
  ...
  netlink_sendmsg (af_netlink.c:1900)

 Freed by task 2519:
  kfree (mm/slub.c:2705 mm/slub.c:6405 mm/slub.c:6720)
  ovs_meter_cmd_set (net/openvswitch/meter.c:479)
  ...
  netlink_sendmsg (af_netlink.c:1900)

Fix that by making sure attach_meter() doesn't make the meter visible
until all the checks are done and the function can't fail anymore.

This also makes sure the "hash" value is calculated after the potential
re-sizing of the table.

Reported by Trend Micro's Zero Day Initiative as ZDI-CAN-31642.

## References
- https://git.kernel.org/stable/c/0310d1fa7f9debd0d89629e9f14c7975a47eaa9a
- https://git.kernel.org/stable/c/431a295d93f76fbdb6a7cfce92a9e3dfee1e5d61
- https://git.kernel.org/stable/c/496f3013c6ff759249abcfb2da2361c1a3e2e66d
- https://git.kernel.org/stable/c/4d03e5fa3fbb1df15258a1eb3d6963f0d65659b3
- https://git.kernel.org/stable/c/90623c9499627803ef3f04fa25a3199402d4fb95
- https://git.kernel.org/stable/c/a58a2b0ce354df531ebc71fc870058c2feb59f6b
- https://git.kernel.org/stable/c/b0de3b58dac3b02b528f72ee0397728aed11f993
- https://git.kernel.org/stable/c/ddc0ef4217cc697c6ba1a295cc1ea42423ec68ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74465.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74465
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
