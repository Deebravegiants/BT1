# [H] net: microchip: vcap: fix races on the shared Super VCAP block

## Summary
Severity: High
Advisory: CVE-2026-72340
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72340
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: microchip: vcap: fix races on the shared Super VCAP block

The VCAP instances on a chip are not independent, yet they are locked
independently. On sparx5 and lan969x the IS0 and IS2 instances are
backed by the same Super VCAP hardware block and share its cache and
command registers: every access drives the shared VCAP_SUPER_CTRL
register and moves data through the shared cache registers.

Accessing one instance therefore races with accessing another. The
per-instance admin->lock cannot prevent this, as each instance takes a
different lock.

The locking issue is mostly disguised by the fact that the core usage of
the vcap api runs under rtnl. However, the full rule dump in debugfs
decodes rules straight from hardware (a READ command followed by a cache
read) and runs outside rtnl, so it races a concurrent tc-flower rule
write to another Super VCAP instance.

Besides corrupting the dump, the read repopulates the shared cache
between the writers cache fill and its write command, so the writer
commits the wrong data and corrupts the hardware entry.

Introduce vcap_lock() and vcap_unlock() helpers and route every rule
lock site in the VCAP API and its debugfs code through them. Replace the
per-instance admin->lock with a single mutex in struct vcap_control that
serializes access to all instances. The helpers reach it through a new
admin->vctrl back-pointer, and the clients initialise and destroy the
control lock instead of a per-instance one.

No path holds more than one instance lock, so collapsing them onto a
single mutex cannot self-deadlock.

## References
- https://git.kernel.org/stable/c/1e71a40d101547380590db582213c1f1dce1f041
- https://git.kernel.org/stable/c/49806bef9572a2e012610517bc14ed0a4db0d1fc
- https://git.kernel.org/stable/c/786456d0a244bbd405dfc60e4de51f8b348b9cb1
- https://git.kernel.org/stable/c/952928564cc5fdb06f92d7e25c6cd2e1d816362b
- https://git.kernel.org/stable/c/d7a8d500d7e42837bd8dce40cb52c97c6e8706a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72340.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
