# [H] CVE-2019-18408

## Summary
Severity: High
Advisory: CVE-2019-18408
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-24
Source: https://osv.dev/vulnerability/CVE-2019-18408
Type: osv

## Details
archive_read_format_rar_read_data in archive_read_support_format_rar.c in libarchive before 3.4.0 has a use-after-free in a certain ARCHIVE_FAILED situation, related to Ppmd7_DecodeSymbol.

## References
- https://support.f5.com/csp/article/K52144175?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6LZ4VJGTCYEJSDLOEWUUFG6TM4SUPFSY/
- https://seclists.org/bugtraq/2019/Nov/2
- https://security.gentoo.org/glsa/202003-28
- https://www.debian.org/security/2019/dsa-4557
- https://access.redhat.com/errata/RHSA-2020:0203
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=14689
- https://github.com/libarchive/libarchive/compare/v3.3.3...v3.4.0
- https://usn.ubuntu.com/4169-1/
- https://lists.debian.org/debian-lts-announce/2019/10/msg00034.html
- https://access.redhat.com/errata/RHSA-2020:0246
- https://access.redhat.com/errata/RHSA-2020:0271
- https://github.com/libarchive/libarchive/commit/b8592ecba2f9e451e1f5cb7ab6dcee8b8e7b3f60
