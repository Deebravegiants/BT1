# [M] CVE-2018-1000880

## Summary
Severity: Medium
Advisory: CVE-2018-1000880
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000880
Type: osv

## Details
libarchive version commit 9693801580c0cf7c70e862d305270a16b52826a7 onwards (release v3.2.0 onwards) contains a CWE-20: Improper Input Validation vulnerability in WARC parser - libarchive/archive_read_support_format_warc.c, _warc_read() that can result in DoS - quasi-infinite run time and disk usage from tiny file. This attack appear to be exploitable via the victim must open a specially crafted WARC file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBOCC2M6YGPZA6US43YK4INPSJZZHRTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W645KCLWFDBDGFJHG57WOVXGE62QSIJI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVXA7PHINVT6DFF6PRLTDTVTXKDLVHNF/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00055.html
- http://www.securityfocus.com/bid/106324
- https://github.com/libarchive/libarchive/pull/1105
- https://usn.ubuntu.com/3859-1/
- https://www.debian.org/security/2018/dsa-4360
- https://bugs.launchpad.net/ubuntu/+source/libarchive/+bug/1794909
- https://github.com/libarchive/libarchive/pull/1105/commits/9c84b7426660c09c18cc349f6d70b5f8168b5680
