# [H] CVE-2016-4580

## Summary
Severity: High
Advisory: CVE-2016-4580
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4580
Type: osv

## Details
The x25_negotiate_facilities function in net/x25/x25_facilities.c in the Linux kernel before 4.5.5 does not properly initialize a certain data structure, which allows attackers to obtain sensitive information from kernel stack memory via an X.25 Call Request.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.5
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.openwall.com/lists/oss-security/2016/05/10/12
- http://www.securityfocus.com/bid/90528
- https://github.com/torvalds/linux/commit/79e48650320e6fba48369fccf13fd045315b19b8
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3017-3
- http://www.ubuntu.com/usn/USN-3018-1
- http://www.ubuntu.com/usn/USN-3018-2
- http://www.ubuntu.com/usn/USN-3017-1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=79e48650320e6fba48369fccf13fd045315b19b8
- http://www.ubuntu.com/usn/USN-3016-3
- http://www.ubuntu.com/usn/USN-3016-4
- http://www.ubuntu.com/usn/USN-3019-1
- http://www.ubuntu.com/usn/USN-3016-2
- http://www.ubuntu.com/usn/USN-3017-2
- http://www.ubuntu.com/usn/USN-3021-1
- http://www.ubuntu.com/usn/USN-3016-1
