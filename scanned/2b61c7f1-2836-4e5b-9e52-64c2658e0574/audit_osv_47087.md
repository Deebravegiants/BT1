# [M] CVE-2015-8915

## Summary
Severity: Medium
Advisory: CVE-2015-8915
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8915
Type: osv

## Details
bsdcpio in libarchive before 3.2.0 allows remote attackers to cause a denial of service (invalid read and crash) via crafted cpio file.

## References
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://security.gentoo.org/glsa/201701-03
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://github.com/libarchive/libarchive/issues/503
- http://www.securityfocus.com/bid/91298
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
