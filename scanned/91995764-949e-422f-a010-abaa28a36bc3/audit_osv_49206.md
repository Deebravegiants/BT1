# [M] CVE-2018-5803

## Summary
Severity: Medium
Advisory: CVE-2018-5803
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-5803
Type: osv

## Details
In the Linux Kernel before version 4.15.8, 4.14.25, 4.9.87, 4.4.121, 4.1.51, and 3.2.102, an error in the "_sctp_make_chunk()" function (net/sctp/sm_make_chunk.c) when handling SCTP packets length can be exploited to cause a kernel crash.

## References
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-2/
- https://www.spinics.net/lists/netdev/msg482523.html
- https://access.redhat.com/errata/RHSA-2018:2948
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.51
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.87
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/commit/?id=07f2c7ab6f8d0a7e7c5764c4e6cc9c52951b9d9c
- https://secuniaresearch.flexerasoftware.com/advisories/81331/
- https://usn.ubuntu.com/3654-1/
- https://usn.ubuntu.com/3697-1/
- https://usn.ubuntu.com/3698-1/
- https://access.redhat.com/errata/RHSA-2018:3083
- https://cdn.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.2.102
- https://usn.ubuntu.com/3654-2/
- https://www.spinics.net/lists/linux-sctp/msg07036.html
- https://access.redhat.com/errata/RHSA-2018:3096
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.25
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3656-1/
- https://usn.ubuntu.com/3697-2/
- https://usn.ubuntu.com/3698-2/
