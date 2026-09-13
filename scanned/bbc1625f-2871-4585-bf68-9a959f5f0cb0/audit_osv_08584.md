# [H] CVE-2016-4485

## Summary
Severity: High
Advisory: CVE-2016-4485
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4485
Type: osv

## Details
The llc_cmsg_rcv function in net/llc/af_llc.c in the Linux kernel before 4.5.5 does not initialize a certain data structure, which allows attackers to obtain sensitive information from kernel stack memory by reading a message.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.securityfocus.com/bid/90015
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-3000-1
- http://www.ubuntu.com/usn/USN-3002-1
- http://www.ubuntu.com/usn/USN-3006-1
- http://www.ubuntu.com/usn/USN-3007-1
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.5
- http://www.ubuntu.com/usn/USN-2989-1
- http://www.ubuntu.com/usn/USN-3001-1
- http://www.ubuntu.com/usn/USN-3003-1
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-3004-1
- http://www.ubuntu.com/usn/USN-2998-1
- http://www.ubuntu.com/usn/USN-3005-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1333309
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b8670c09f37bdf2847cc44f36511a53afc6161fd
