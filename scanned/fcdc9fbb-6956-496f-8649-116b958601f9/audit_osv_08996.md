# [M] CVE-2016-7166

## Summary
Severity: Medium
Advisory: CVE-2016-7166
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-7166
Type: osv

## Details
libarchive before 3.2.0 does not limit the number of recursive decompressions, which allows remote attackers to cause a denial of service (memory consumption and application crash) via a crafted gzip file.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://rhn.redhat.com/errata/RHSA-2016-1850.html
- http://www.openwall.com/lists/oss-security/2016/09/08/15
- http://www.openwall.com/lists/oss-security/2016/09/08/18
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.securityfocus.com/bid/92901
- https://security.gentoo.org/glsa/201701-03
- https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=207362
- https://bugzilla.redhat.com/show_bug.cgi?id=1347086
- https://github.com/libarchive/libarchive/commit/6e06b1c89dd0d16f74894eac4cfc1327a06ee4a0
- https://github.com/libarchive/libarchive/issues/660
