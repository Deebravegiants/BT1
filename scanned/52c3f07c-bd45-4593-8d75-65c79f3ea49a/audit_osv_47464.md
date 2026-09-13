# [H] CVE-2016-5828

## Summary
Severity: High
Advisory: CVE-2016-5828
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-5828
Type: osv

## Details
The start_thread function in arch/powerpc/kernel/process.c in the Linux kernel through 4.6.3 on powerpc platforms mishandles transactional state, which allows local users to cause a denial of service (invalid process state or TM Bad Thing exception, and system crash) or possibly have unspecified other impact by starting and suspending a transaction before an exec system call.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.ubuntu.com/usn/USN-3070-2
- http://www.ubuntu.com/usn/USN-3071-2
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://www.debian.org/security/2016/dsa-3616
- http://www.openwall.com/lists/oss-security/2016/06/25/7
- http://www.securityfocus.com/bid/91415
- http://www.ubuntu.com/usn/USN-3070-1
- http://www.ubuntu.com/usn/USN-3070-3
- http://www.ubuntu.com/usn/USN-3070-4
- http://www.ubuntu.com/usn/USN-3071-1
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- https://patchwork.ozlabs.org/patch/636776/
