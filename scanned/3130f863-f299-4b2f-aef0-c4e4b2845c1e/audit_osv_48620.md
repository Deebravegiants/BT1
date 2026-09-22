# [M] CVE-2018-10087

## Summary
Severity: Medium
Advisory: CVE-2018-10087
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-13
Source: https://osv.dev/vulnerability/CVE-2018-10087
Type: osv

## Details
The kernel_wait4 function in kernel/exit.c in the Linux kernel before 4.13, when an unspecified architecture and compiler is used, might allow local users to cause a denial of service by triggering an attempted use of the -INT_MIN value.

## References
- http://www.securityfocus.com/bid/103774
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://news.ycombinator.com/item?id=2972021
- https://usn.ubuntu.com/3696-1/
- https://usn.ubuntu.com/3696-2/
- https://usn.ubuntu.com/3754-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dd83c161fbcc5d8be637ab159c0de015cbff5ba4
- https://github.com/torvalds/linux/commit/dd83c161fbcc5d8be637ab159c0de015cbff5ba4
