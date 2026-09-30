# [H] CVE-2018-1000877

## Summary
Severity: High
Advisory: CVE-2018-1000877
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000877
Type: osv

## Details
libarchive version commit 416694915449219d505531b1096384f3237dd6cc onwards (release v3.1.0 onwards) contains a CWE-415: Double Free vulnerability in RAR decoder - libarchive/archive_read_support_format_rar.c, parse_codes(), realloc(rar->lzss.window, new_size) with new_size = 0 that can result in Crash/DoS. This attack appear to be exploitable via the victim must open a specially crafted RAR archive.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBOCC2M6YGPZA6US43YK4INPSJZZHRTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W645KCLWFDBDGFJHG57WOVXGE62QSIJI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVXA7PHINVT6DFF6PRLTDTVTXKDLVHNF/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00055.html
- http://www.securityfocus.com/bid/106324
- https://access.redhat.com/errata/RHSA-2019:2298
- https://access.redhat.com/errata/RHSA-2019:3698
- https://bugs.launchpad.net/ubuntu/+source/libarchive/+bug/1794909
- https://github.com/libarchive/libarchive/pull/1105
- https://lists.debian.org/debian-lts-announce/2018/12/msg00011.html
- https://usn.ubuntu.com/3859-1/
- https://www.debian.org/security/2018/dsa-4360
- https://github.com/libarchive/libarchive/pull/1105/commits/021efa522ad729ff0f5806c4ce53e4a6cc1daa31
