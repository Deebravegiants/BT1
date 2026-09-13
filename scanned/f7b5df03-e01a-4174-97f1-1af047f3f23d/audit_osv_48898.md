# [M] CVE-2018-17972

## Summary
Severity: Medium
Advisory: CVE-2018-17972
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-03
Source: https://osv.dev/vulnerability/CVE-2018-17972
Type: osv

## Details
An issue was discovered in the proc_pid_stack function in fs/proc/base.c in the Linux kernel through 4.18.11. It does not ensure that only root may inspect the kernel stack of an arbitrary task, allowing a local attacker to exploit racy stack unwinding and leak kernel task stack contents.

## References
- https://support.f5.com/csp/article/K27673650?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00043.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://usn.ubuntu.com/3821-2/
- https://access.redhat.com/errata/RHSA-2019:2473
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3832-1/
- https://usn.ubuntu.com/3871-4/
- https://access.redhat.com/errata/RHSA-2019:0514
- https://access.redhat.com/errata/RHSA-2019:0831
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3880-2/
- https://access.redhat.com/errata/RHSA-2019:0512
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://usn.ubuntu.com/3821-1/
- https://usn.ubuntu.com/3835-1/
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-5/
- https://usn.ubuntu.com/3880-1/
- http://www.securityfocus.com/bid/105525
