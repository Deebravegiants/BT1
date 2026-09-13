# [M] CVE-2016-1237

## Summary
Severity: Medium
Advisory: CVE-2016-1237
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-29
Source: https://osv.dev/vulnerability/CVE-2016-1237
Type: osv

## Details
nfsd in the Linux kernel through 4.6.3 allows local users to bypass intended file-permission restrictions by setting a POSIX ACL, related to nfs2acl.c, nfs3acl.c, and nfs4acl.c.

## References
- http://www.securityfocus.com/bid/91456
- http://www.openwall.com/lists/oss-security/2016/06/25/2
- http://www.ubuntu.com/usn/USN-3053-1
- http://www.ubuntu.com/usn/USN-3070-3
- http://www.ubuntu.com/usn/USN-3070-4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=999653786df6954a31044528ac3f7a5dadca08f4
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3070-1
- http://www.ubuntu.com/usn/USN-3070-2
- https://github.com/torvalds/linux/commit/999653786df6954a31044528ac3f7a5dadca08f4
- https://bugzilla.redhat.com/show_bug.cgi?id=1350845
