# [M] CVE-2016-8688

## Summary
Severity: Medium
Advisory: CVE-2016-8688
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8688
Type: osv

## Details
The mtree bidder in libarchive 3.2.1 does not keep track of line sizes when extending the read-ahead, which allows remote attackers to cause a denial of service (crash) via a crafted file, which triggers an invalid read in the (1) detect_form or (2) bid_entry function in libarchive/archive_read_support_format_mtree.c.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00027.html
- http://www.securityfocus.com/bid/93781
- http://www.openwall.com/lists/oss-security/2016/10/16/11
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-heap-based-buffer-overflow-in-bid_entry-archive_read_support_format_mtree-c/
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-heap-based-buffer-overflow-in-detect_form-archive_read_support_format_mtree-c/
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-memory-corruptionunknown-crash-in-bid_entry-archive_read_support_format_mtree-c/
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-use-after-free-in-bid_entry-archive_read_support_format_mtree-c/
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-use-after-free-in-detect_form-archive_read_support_format_mtree-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1377923
- https://github.com/libarchive/libarchive/commit/eec077f52bfa2d3f7103b4b74d52572ba8a15aca
- https://security.gentoo.org/glsa/201701-03
