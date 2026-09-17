# [M] CVE-2016-4578

## Summary
Severity: Medium
Advisory: CVE-2016-4578
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4578
Type: osv

## Details
sound/core/timer.c in the Linux kernel through 4.6 does not initialize certain r1 data structures, which allows local users to obtain sensitive information from kernel stack memory via crafted use of the ALSA timer interface, related to the (1) snd_timer_user_ccallback and (2) snd_timer_user_tinterrupt functions.

## References
- http://www.ubuntu.com/usn/USN-3021-1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9a47e9cff994f37f7f0dbd9ae23740d0f64f9fe6
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3016-4
- https://github.com/torvalds/linux/commit/9a47e9cff994f37f7f0dbd9ae23740d0f64f9fe6
- http://www.ubuntu.com/usn/USN-3018-2
- http://www.ubuntu.com/usn/USN-3021-2
- http://www.ubuntu.com/usn/USN-3017-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.ubuntu.com/usn/USN-3016-2
- http://www.ubuntu.com/usn/USN-3017-2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e4ec8cc8039a7063e24204299b462bd1383184a5
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://www.ubuntu.com/usn/USN-3016-1
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://www.ubuntu.com/usn/USN-3020-1
