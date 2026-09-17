# [M] CVE-2018-10124

## Summary
Severity: Medium
Advisory: CVE-2018-10124
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-10124
Type: osv

## Details
The kill_something_info function in kernel/signal.c in the Linux kernel before 4.13, when an unspecified architecture and compiler is used, might allow local users to cause a denial of service via an INT_MIN argument.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3696-1/
- https://usn.ubuntu.com/3696-2/
- https://usn.ubuntu.com/3754-1/
- http://www.securitytracker.com/id/1040684
- https://github.com/torvalds/linux/commit/4ea77014af0d6205b05503d1c7aac6eace11d473
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4ea77014af0d6205b05503d1c7aac6eace11d473
- https://news.ycombinator.com/item?id=2972021
