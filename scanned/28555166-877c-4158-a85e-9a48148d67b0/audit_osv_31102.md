# [M] CVE-2024-57970

## Summary
Severity: Medium
Advisory: CVE-2024-57970
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-16
Source: https://osv.dev/vulnerability/CVE-2024-57970
Type: osv

## Details
libarchive through 3.7.7 has a heap-based buffer over-read in header_gnu_longlink in archive_read_support_format_tar.c via a TAR archive because it mishandles truncation in the middle of a GNU long linkname.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57970.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57970
- https://github.com/libarchive/libarchive/issues/2415
- https://github.com/libarchive/libarchive/pull/2422
