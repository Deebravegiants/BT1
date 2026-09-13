# [M] CVE-2015-8923

## Summary
Severity: Medium
Advisory: CVE-2015-8923
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8923
Type: osv

## Details
The process_extra function in libarchive before 3.2.0 uses the size field and a signed number in an offset, which allows remote attackers to cause a denial of service (crash) via a crafted zip file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- http://www.ubuntu.com/usn/USN-3033-1
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://security.gentoo.org/glsa/201701-03
- https://github.com/libarchive/libarchive/issues/514
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91309
