# [M] CVE-2016-5844

## Summary
Severity: Medium
Advisory: CVE-2016-5844
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-5844
Type: osv

## Details
Integer overflow in the ISO parser in libarchive before 3.2.1 allows remote attackers to cause a denial of service (application crash) via a crafted ISO file.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://rhn.redhat.com/errata/RHSA-2016-1850.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91808
- http://www.securitytracker.com/id/1036173
- https://security.gentoo.org/glsa/201701-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1350280
- http://www.openwall.com/lists/oss-security/2016/06/23/6
- http://www.openwall.com/lists/oss-security/2016/06/24/4
- https://blog.fuzzing-project.org/48-Out-of-bounds-read-and-signed-integer-overflow-in-libarchive.html
- https://github.com/libarchive/libarchive/commit/3ad08e01b4d253c66ae56414886089684155af22
- https://github.com/libarchive/libarchive/issues/717
