# [M] CVE-2019-14283

## Summary
Severity: Medium
Advisory: CVE-2019-14283
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2019-14283
Type: osv

## Details
In the Linux kernel before 5.2.3, set_geometry in drivers/block/floppy.c does not validate the sect and head fields, as demonstrated by an integer overflow and out-of-bounds read. It can be triggered by an unprivileged local user when a floppy disk has been inserted. NOTE: QEMU creates the floppy device by default.

## References
- https://seclists.org/bugtraq/2019/Aug/18
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4117-1/
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4114-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00056.html
- http://packetstormsecurity.com/files/154408/Kernel-Live-Patch-Security-Notice-LSN-0055-1.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://seclists.org/bugtraq/2019/Aug/26
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00055.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://usn.ubuntu.com/4116-1/
- http://packetstormsecurity.com/files/154059/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3
- https://www.debian.org/security/2019/dsa-4495
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://www.debian.org/security/2019/dsa-4497
- https://github.com/torvalds/linux/commit/da99466ac243f15fbba65bd261bfc75ffa1532b6
