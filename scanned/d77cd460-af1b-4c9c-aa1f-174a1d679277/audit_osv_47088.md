# [M] CVE-2015-8916

## Summary
Severity: Medium
Advisory: CVE-2015-8916
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8916
Type: osv

## Details
bsdtar in libarchive before 3.2.0 returns a success code without filling the entry when the header is a "split file in multivolume RAR," which allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted rar file.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- http://www.ubuntu.com/usn/USN-3033-1
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://security-tracker.debian.org/tracker/CVE-2015-8916
- https://security.gentoo.org/glsa/201701-03
- https://github.com/libarchive/libarchive/issues/504
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/91296
