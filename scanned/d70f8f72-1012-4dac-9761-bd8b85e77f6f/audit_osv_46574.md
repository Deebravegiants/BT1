# [M] CVE-2013-7446

## Summary
Severity: Medium
Advisory: CVE-2013-7446
CVSS: 5.3 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2015-12-28
Source: https://osv.dev/vulnerability/CVE-2013-7446
Type: osv

## Details
Use-after-free vulnerability in net/unix/af_unix.c in the Linux kernel before 4.3.3 allows local users to bypass intended AF_UNIX socket permissions or cause a denial of service (panic) via crafted epoll_ctl calls.

## References
- http://www.debian.org/security/2015/dsa-3426
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.3
- http://www.ubuntu.com/usn/USN-2886-1
- http://www.ubuntu.com/usn/USN-2887-1
- http://www.ubuntu.com/usn/USN-2887-2
- http://www.ubuntu.com/usn/USN-2888-1
- http://www.ubuntu.com/usn/USN-2889-1
- http://www.ubuntu.com/usn/USN-2889-2
- http://www.ubuntu.com/usn/USN-2890-1
- http://www.ubuntu.com/usn/USN-2890-2
- http://www.ubuntu.com/usn/USN-2890-3
- https://github.com/torvalds/linux/commit/7d267278a9ece963d77eefec61630223fce08c6c
- http://www.spinics.net/lists/netdev/msg318826.html
- https://lkml.org/lkml/2013/10/14/424
- https://lkml.org/lkml/2014/5/15/532
- https://lkml.org/lkml/2015/9/13/195
- https://bugzilla.redhat.com/show_bug.cgi?id=1282688
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7d267278a9ece963d77eefec61630223fce08c6c
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00034.html
