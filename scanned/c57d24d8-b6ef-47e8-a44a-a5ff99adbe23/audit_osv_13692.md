# [H] CVE-2018-20836

## Summary
Severity: High
Advisory: CVE-2018-20836
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-07
Source: https://osv.dev/vulnerability/CVE-2018-20836
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.20. There is a race condition in smp_task_timedout() and smp_task_done() in drivers/scsi/libsas/sas_expander.c, leading to a use-after-free.

## References
- https://support.f5.com/csp/article/K11225249
- https://usn.ubuntu.com/4076-1/
- https://www.debian.org/security/2019/dsa-4495
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00025.html
- https://seclists.org/bugtraq/2019/Aug/13
- https://seclists.org/bugtraq/2019/Aug/18
- https://security.netapp.com/advisory/ntap-20190719-0003/
- https://www.debian.org/security/2019/dsa-4497
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00014.html
- http://www.securityfocus.com/bid/108196
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b90cd6f2b905905fb42671009dc0e27c310a16ae
- https://github.com/torvalds/linux/commit/b90cd6f2b905905fb42671009dc0e27c310a16ae
