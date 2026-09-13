# [M] CVE-2015-8929

## Summary
Severity: Medium
Advisory: CVE-2015-8929
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8929
Type: osv

## Details
Memory leak in the __archive_read_get_extract function in archive_read_extract2.c in libarchive before 3.2.0 allows remote attackers to cause a denial of service via a tar file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00025.html
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://github.com/libarchive/libarchive/issues/517
- https://security.gentoo.org/glsa/201701-03
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- https://github.com/libarchive/libarchive/issues/517
- https://github.com/libarchive/libarchive/issues/517
- http://www.securityfocus.com/bid/91340
