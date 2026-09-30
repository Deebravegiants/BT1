# [M] CVE-2019-13648

## Summary
Severity: Medium
Advisory: CVE-2019-13648
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/CVE-2019-13648
Type: osv

## Details
In the Linux kernel through 5.2.1 on the powerpc platform, when hardware transactional memory is disabled, a local user can cause a denial of service (TM Bad Thing exception and system crash) via a sigreturn() system call that sends a crafted signal frame. This affects arch/powerpc/kernel/signal_32.c and arch/powerpc/kernel/signal_64.c.

## References
- https://usn.ubuntu.com/4114-1/
- https://usn.ubuntu.com/4115-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00056.html
- http://packetstormsecurity.com/files/154059/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://usn.ubuntu.com/4116-1/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GRK2MW223KQZ76DKEF2BZFN6TCXLZLDS/
- https://seclists.org/bugtraq/2019/Aug/18
- https://seclists.org/bugtraq/2019/Aug/26
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00055.html
- http://www.openwall.com/lists/oss-security/2019/07/30/1
- https://git.kernel.org/torvalds/c/f16d80b75a096c52354c6e0a574993f3b0dfbdfe
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://security.netapp.com/advisory/ntap-20190806-0001/
- https://www.debian.org/security/2019/dsa-4497
- https://www.debian.org/security/2019/dsa-4495
- https://patchwork.ozlabs.org/patch/1133904/
