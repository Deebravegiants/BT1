# [M] CVE-2018-12896

## Summary
Severity: Medium
Advisory: CVE-2018-12896
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-02
Source: https://osv.dev/vulnerability/CVE-2018-12896
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.3. An Integer Overflow in kernel/time/posix-timers.c in the POSIX timer code is caused by the way the overrun accounting works. Depending on interval and expiry time values, the overrun can be larger than INT_MAX, but the accounting is int based. This basically makes the accounting values, which are visible to user space via timer_getoverrun(2) and siginfo::si_overrun, random. For example, a local user can cause a denial of service (signed integer overflow) via crafted mmap, futex, timer_create, and timer_settime system calls.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3847-1/
- https://usn.ubuntu.com/3847-3/
- https://usn.ubuntu.com/3848-2/
- https://usn.ubuntu.com/3849-2/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://usn.ubuntu.com/3847-2/
- https://usn.ubuntu.com/3848-1/
- https://usn.ubuntu.com/3849-1/
- https://bugzilla.kernel.org/show_bug.cgi?id=200189
- https://github.com/torvalds/linux/commit/78c9c4dfbf8c04883941445a195276bb4bb92c76
- https://github.com/lcytxw/bug_repro/tree/master/bug_200189
