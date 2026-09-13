# [M] CVE-2014-7975

## Summary
Severity: Medium
Advisory: CVE-2014-7975
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-10-13
Source: https://osv.dev/vulnerability/CVE-2014-7975
Type: osv

## Details
The do_umount function in fs/namespace.c in the Linux kernel through 3.17 does not require the CAP_SYS_ADMIN capability for do_remount_sb calls that change the root filesystem to read-only, which allows local users to cause a denial of service (loss of writability) by making certain unshare system calls, clearing the / MNT_LOCKED flag, and making an MNT_FORCE umount system call.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0ef3a56b1c466629cd0bf482b09c7b0e5a085bb5
- http://secunia.com/advisories/60174
- http://secunia.com/advisories/61145
- http://secunia.com/advisories/62633
- http://secunia.com/advisories/62634
- http://www.openwall.com/lists/oss-security/2014/10/08/22
- http://www.securityfocus.com/bid/70314
- http://www.securitytracker.com/id/1031180
- http://www.ubuntu.com/usn/USN-2415-1
- http://www.ubuntu.com/usn/USN-2416-1
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- http://www.ubuntu.com/usn/USN-2419-1
- http://www.ubuntu.com/usn/USN-2420-1
- http://www.ubuntu.com/usn/USN-2421-1
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://bugzilla.redhat.com/show_bug.cgi?id=1151108
- https://exchange.xforce.ibmcloud.com/vulnerabilities/96994
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0ef3a56b1c466629cd0bf482b09c7b0e5a085bb5
