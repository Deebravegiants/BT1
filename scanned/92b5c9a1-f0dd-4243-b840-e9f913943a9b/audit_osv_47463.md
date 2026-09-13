# [M] CVE-2016-5728

## Summary
Severity: Medium
Advisory: CVE-2016-5728
CVSS: 6.3 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-5728
Type: osv

## Details
Race condition in the vop_ioctl function in drivers/misc/mic/vop/vop_vringh.c in the MIC VOP driver in the Linux kernel before 4.6.1 allows local users to obtain sensitive information from kernel memory or cause a denial of service (memory corruption and system crash) by changing a certain header, aka a "double fetch" vulnerability.

## References
- http://www.securityfocus.com/archive/1/538802/30/0/threaded
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.1
- http://www.ubuntu.com/usn/USN-3070-1
- http://www.ubuntu.com/usn/USN-3070-2
- http://www.ubuntu.com/usn/USN-3070-3
- http://www.ubuntu.com/usn/USN-3070-4
- http://www.ubuntu.com/usn/USN-3071-1
- https://github.com/torvalds/linux/commit/9bf292bfca94694a721449e3fd752493856710f6
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9bf292bfca94694a721449e3fd752493856710f6
- http://www.debian.org/security/2016/dsa-3616
- http://www.ubuntu.com/usn/USN-3071-2
- https://bugzilla.kernel.org/show_bug.cgi?id=116651
