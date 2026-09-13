# [M] CVE-2019-1000020

## Summary
Severity: Medium
Advisory: CVE-2019-1000020
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000020
Type: osv

## Details
libarchive version commit 5a98dcf8a86364b3c2c469c85b93647dfb139961 onwards (version v2.8.0 onwards) contains a CWE-835: Loop with Unreachable Exit Condition ('Infinite Loop') vulnerability in ISO9660 parser, archive_read_support_format_iso9660.c, read_CE()/parse_rockridge() that can result in DoS by infinite loop. This attack appears to be exploitable via the victim opening a specially crafted ISO9660 file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBOCC2M6YGPZA6US43YK4INPSJZZHRTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVXA7PHINVT6DFF6PRLTDTVTXKDLVHNF/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00055.html
- https://access.redhat.com/errata/RHSA-2019:2298
- https://access.redhat.com/errata/RHSA-2019:3698
- https://github.com/libarchive/libarchive/pull/1120
- https://lists.debian.org/debian-lts-announce/2019/02/msg00013.html
- https://usn.ubuntu.com/3884-1/
- https://github.com/libarchive/libarchive/pull/1120/commits/8312eaa576014cd9b965012af51bc1f967b12423
