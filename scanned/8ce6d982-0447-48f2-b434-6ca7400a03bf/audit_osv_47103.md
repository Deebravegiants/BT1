# [M] CVE-2015-8933

## Summary
Severity: Medium
Advisory: CVE-2015-8933
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8933
Type: osv

## Details
Integer overflow in the archive_read_format_tar_skip function in archive_read_support_format_tar.c in libarchive before 3.2.0 allows remote attackers to cause a denial of service (crash) via a crafted tar file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00025.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- http://www.ubuntu.com/usn/USN-3033-1
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://github.com/libarchive/libarchive/issues/548
- https://security.gentoo.org/glsa/201701-03
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- https://github.com/libarchive/libarchive/issues/548
- https://github.com/libarchive/libarchive/issues/548
- https://github.com/libarchive/libarchive/issues/548
- http://www.securityfocus.com/bid/91421
