# [H] CVE-2016-5418

## Summary
Severity: High
Advisory: CVE-2016-5418
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-5418
Type: osv

## Details
The sandboxing code in libarchive 3.2.0 and earlier mishandles hardlink archive entries of non-zero data size, which might allow remote attackers to write to arbitrary files via a crafted archive file.

## References
- http://www.securityfocus.com/bid/93165
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://rhn.redhat.com/errata/RHSA-2016-1850.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- https://access.redhat.com/errata/RHSA-2016:1852
- https://access.redhat.com/errata/RHSA-2016:1853
- https://security.gentoo.org/glsa/201701-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1362601
- https://github.com/libarchive/libarchive/commit/dfd6b54ce33960e420fb206d8872fb759b577ad9
- https://github.com/libarchive/libarchive/issues/746
- http://www.openwall.com/lists/oss-security/2016/08/09/2
- https://gist.github.com/anonymous/e48209b03f1dd9625a992717e7b89c4f
