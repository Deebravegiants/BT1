# [H] CVE-2020-9308

## Summary
Severity: High
Advisory: CVE-2020-9308
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-20
Source: https://osv.dev/vulnerability/CVE-2020-9308
Type: osv

## Details
archive_read_support_format_rar5.c in libarchive before 3.4.2 attempts to unpack a RAR5 file with an invalid or corrupted header (such as a header size of zero), leading to a SIGSEGV or possibly unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6OTE7GWASH2ZOVG5H3HEN5PR6B3KF7JB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J76F7VU7HC3GBKG5SAKTRBOFOI3RGO6M/
- https://security.gentoo.org/glsa/202003-28
- https://usn.ubuntu.com/4293-1/
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=20459
- https://github.com/libarchive/libarchive/pull/1326
- https://github.com/libarchive/libarchive/pull/1326/commits/94821008d6eea81e315c5881cdf739202961040a
