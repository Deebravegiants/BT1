# [M] CVE-2019-14284

## Summary
Severity: Medium
Advisory: CVE-2019-14284
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-26
Source: https://osv.dev/vulnerability/CVE-2019-14284
Type: osv

## Details
In the Linux kernel before 5.2.3, drivers/block/floppy.c allows a denial of service by setup_format_params division-by-zero. Two consecutive ioctls can trigger the bug: the first one should set the drive geometry with .sect and .rate values that make F_SECT_PER_TRACK be zero. Next, the floppy format operation should be called. It can be triggered by an unprivileged local user even when a floppy disk has not been inserted. NOTE: QEMU creates the floppy device by default.

## References
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://seclists.org/bugtraq/2019/Aug/18
- https://usn.ubuntu.com/4116-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00055.html
- http://packetstormsecurity.com/files/154059/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- http://packetstormsecurity.com/files/154408/Kernel-Live-Patch-Security-Notice-LSN-0055-1.html
- https://usn.ubuntu.com/4117-1/
- https://usn.ubuntu.com/4114-1/
- https://usn.ubuntu.com/4118-1/
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://seclists.org/bugtraq/2019/Aug/26
- https://usn.ubuntu.com/4115-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00056.html
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3
- https://www.debian.org/security/2019/dsa-4495
- https://www.debian.org/security/2019/dsa-4497
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f3554aeb991214cbfafd17d55e2bfddb50282e32
