# [M] CVE-2022-47929

## Summary
Severity: Medium
Advisory: CVE-2022-47929
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-47929
Type: osv

## Details
In the Linux kernel before 6.1.6, a NULL pointer dereference bug in the traffic control subsystem allows an unprivileged user to trigger a denial of service (system crash) via a crafted traffic control configuration that is set up with "tc qdisc" and "tc class" commands. This affects qdisc_graft in net/sched/sch_api.c.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://tldp.org/HOWTO/Traffic-Control-HOWTO/components.html
- https://www.debian.org/security/2023/dsa-5324
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=96398560f26aa07e8f2969d73c8197e6a6d10407
- https://www.spinics.net/lists/netdev/msg555705.html
