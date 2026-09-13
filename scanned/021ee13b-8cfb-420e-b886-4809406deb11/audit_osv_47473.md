# [M] CVE-2016-6197

## Summary
Severity: Medium
Advisory: CVE-2016-6197
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6197
Type: osv

## Details
fs/overlayfs/dir.c in the OverlayFS filesystem implementation in the Linux kernel before 4.6 does not properly verify the upper dentry before proceeding with unlink and rename system-call processing, which allows local users to cause a denial of service (system crash) via a rename system call that specifies a self-hardlink.

## References
- http://www.securityfocus.com/bid/91709
- http://www.securitytracker.com/id/1036273
- http://rhn.redhat.com/errata/RHSA-2016-1847.html
- http://rhn.redhat.com/errata/RHSA-2016-1875.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.ubuntu.com/usn/USN-3070-1
- http://www.ubuntu.com/usn/USN-3070-2
- http://www.openwall.com/lists/oss-security/2016/07/11/8
- http://www.ubuntu.com/usn/USN-3070-3
- http://www.ubuntu.com/usn/USN-3070-4
- https://bugzilla.redhat.com/show_bug.cgi?id=1355650
- https://github.com/torvalds/linux/commit/11f3710417d026ea2f4fcf362d866342c5274185
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=11f3710417d026ea2f4fcf362d866342c5274185
