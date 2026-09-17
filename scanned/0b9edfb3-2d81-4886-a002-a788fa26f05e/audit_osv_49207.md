# [H] CVE-2018-5814

## Summary
Severity: High
Advisory: CVE-2018-5814
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-5814
Type: osv

## Details
In the Linux Kernel before version 4.16.11, 4.14.43, 4.9.102, and 4.4.133, multiple race condition errors when handling probe, disconnect, and rebind operations can be exploited to trigger a use-after-free condition or a NULL pointer dereference by sending multiple USB over IP packets.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00043.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.102
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://secuniaresearch.flexerasoftware.com/advisories/81540/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- http://www.securitytracker.com/id/1041050
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.11
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.133
- https://usn.ubuntu.com/3696-2/
- https://usn.ubuntu.com/3752-1/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.43
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-8/
- https://usn.ubuntu.com/3696-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/commit/?id=22076557b07c12086eeb16b8ce2b0b735f7a27e7
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git/commit/?id=c171654caa875919be3c533d3518da8be5be966e
