# [H] CVE-2016-8689

## Summary
Severity: High
Advisory: CVE-2016-8689
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8689
Type: osv

## Details
The read_Header function in archive_read_support_format_7zip.c in libarchive 3.2.1 allows remote attackers to cause a denial of service (out-of-bounds read) via multiple EmptyStream attributes in a header in a 7zip archive.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00027.html
- http://www.securityfocus.com/bid/93781
- http://www.openwall.com/lists/oss-security/2016/10/16/11
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-heap-based-buffer-overflow-in-read_header-archive_read_support_format_7zip-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1377925
- https://github.com/libarchive/libarchive/commit/7f17c791dcfd8c0416e2cd2485b19410e47ef126
- https://security.gentoo.org/glsa/201701-03
