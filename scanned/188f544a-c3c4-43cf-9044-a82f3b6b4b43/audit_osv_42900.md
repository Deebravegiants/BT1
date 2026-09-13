# [H] can: bcm: fix lockless bound/ifindex race and silent RX_SETUP failure

## Summary
Severity: High
Advisory: CVE-2026-72122
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72122
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: fix lockless bound/ifindex race and silent RX_SETUP failure

bcm_sendmsg() reads bo->ifindex and checks bo->bound before taking
lock_sock(), while bcm_notify(), bcm_connect() and bcm_release() all
mutate both fields under that same lock. Because the lockless reads
and the locked writes are unordered with respect to each other, a
racing bcm_notify() (device unregister) or bcm_connect() (concurrent
bind on another thread sharing the socket) can make bcm_sendmsg()
observe an inconsistent combination, e.g. a stale bound=1 together
with the now-cleared ifindex=0, silently turning a socket bound to a
specific CAN interface into one that also matches "any" interface.

Keep the lockless bo->bound check purely as a fast-path reject, and
move the ifindex read (and a bo->bound re-check) into the locked
section, where every writer already serializes. This removes the
possibility of observing the two fields torn against each other,
rather than trying to fix it with more READ_ONCE()/WRITE_ONCE() pairs
on two independently updated fields. Annotate the now-purely-lockless
bo->bound accesses consistently across all its write sites.

Also fix bcm_rx_setup() silently returning success when the target
device disappears concurrently instead of reporting -ENODEV, so a
broken RX op is no longer left registered as if it had succeeded.

## References
- https://git.kernel.org/stable/c/0f6f9f95294b4cbb26ba02209e893e3bd91237c3
- https://git.kernel.org/stable/c/35f0ac19efb1a3f6c5e12c00e475a9ec2d9c3a6d
- https://git.kernel.org/stable/c/6bcc5cd247c2934373bc2a1cdf8bf12321169543
- https://git.kernel.org/stable/c/9e60c586faeaed80d55ab8ce2a4b8e56133bc395
- https://git.kernel.org/stable/c/b70f1a15533afeeec5d07f20bec3f3867ab1c7b6
- https://git.kernel.org/stable/c/b9c6ac6fb4e01b34575816066e5d3890a57b3c86
- https://git.kernel.org/stable/c/d9b091d9d22fee81ec53fb55d2032951993ceadb
- https://git.kernel.org/stable/c/ffa80a2af27c97453861a5128e537214a31cd18a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72122.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72122
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
