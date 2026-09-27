# [M] CVE-2020-27675

## Summary
Severity: Medium
Advisory: CVE-2020-27675
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-22
Source: https://osv.dev/vulnerability/CVE-2020-27675
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.9.1, as used with Xen through 4.14.x. drivers/xen/events/events_base.c allows event-channel removal during the event-handling loop (a race condition). This can cause a use-after-free or NULL pointer dereference, as demonstrated by a dom0 crash via events for an in-reconfiguration paravirtualized device, aka CID-073d0552ead5.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3ZG6TZLD23QO3PV2AN2HB625ZX47ALTT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6USZ4APZSBQDHGJLJMHW5JBN4QZV6SKZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GNF2R7FUT4IOJ2RIRGQ7X5R4F4FVVLSR/
- http://www.openwall.com/lists/oss-security/2021/01/19/3
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://security.gentoo.org/glsa/202011-06
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://xenbits.xen.org/xsa/advisory-331.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=073d0552ead5bfc7a3a9c01de590e924f11b5dd2
- https://github.com/torvalds/linux/commit/073d0552ead5bfc7a3a9c01de590e924f11b5dd2
