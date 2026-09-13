# [M] CVE-2015-8922

## Summary
Severity: Medium
Advisory: CVE-2015-8922
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8922
Type: osv

## Details
The read_CodersInfo function in archive_read_support_format_7zip.c in libarchive before 3.2.0 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted 7z file, related to the _7z_folder struct.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.ubuntu.com/usn/USN-3033-1
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://security.gentoo.org/glsa/201701-03
- https://www.suse.com/security/cve/CVE-2015-8922.html
- https://github.com/libarchive/libarchive/issues/513
- http://www.securityfocus.com/bid/91312
