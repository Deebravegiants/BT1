# [M] CVE-2016-4569

## Summary
Severity: Medium
Advisory: CVE-2016-4569
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4569
Type: osv

## Details
The snd_timer_user_params function in sound/core/timer.c in the Linux kernel through 4.6 does not initialize a certain data structure, which allows local users to obtain sensitive information from kernel stack memory via crafted use of the ALSA timer interface.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://www.openwall.com/lists/oss-security/2016/05/09/17
- http://www.securityfocus.com/bid/90347
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cec8f96e49d9be372fdb0c3836dcf31ec71e457e
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://www.ubuntu.com/usn/USN-3017-3
- http://www.ubuntu.com/usn/USN-3020-1
- https://github.com/torvalds/linux/commit/cec8f96e49d9be372fdb0c3836dcf31ec71e457e
- http://www.ubuntu.com/usn/USN-3016-4
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.ubuntu.com/usn/USN-3018-2
- http://www.ubuntu.com/usn/USN-3019-1
- http://www.ubuntu.com/usn/USN-3016-1
- http://www.ubuntu.com/usn/USN-3017-1
- http://www.debian.org/security/2016/dsa-3607
