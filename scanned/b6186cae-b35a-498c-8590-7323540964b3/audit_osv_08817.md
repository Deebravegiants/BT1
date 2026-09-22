# [H] CVE-2016-6250

## Summary
Severity: High
Advisory: CVE-2016-6250
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-6250
Type: osv

## Details
Integer overflow in the ISO9660 writer in libarchive before 3.2.1 allows remote attackers to cause a denial of service (application crash) or execute arbitrary code via vectors related to verifying filename lengths when writing an ISO9660 archive, which trigger a buffer overflow.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.openwall.com/lists/oss-security/2016/07/20/1
- http://www.openwall.com/lists/oss-security/2016/07/21/3
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/92036
- http://www.securitytracker.com/id/1036431
- https://security.gentoo.org/glsa/201701-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1347085
- https://github.com/libarchive/libarchive/files/295073/libarchiveOverflow.txt
- https://github.com/libarchive/libarchive/commit/3014e198
- https://github.com/libarchive/libarchive/issues/711
