# [M] libarchive through 3.7.7 has a heap-based buffer over-read in `header_gnu_longlink` in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-250
Ecosystem: Julia
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-250
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.9+0

## Details
libarchive through 3.7.7 has a heap-based buffer over-read in `header_gnu_longlink` in `archive_read_support_format_tar.c` via a TAR archive because it mishandles truncation in the middle of a GNU long linkname.

## References
- https://github.com/advisories/GHSA-2q66-6w43-8rm9
- https://github.com/libarchive/libarchive/issues/2415
- https://github.com/libarchive/libarchive/pull/2422
- https://nvd.nist.gov/vuln/detail/CVE-2024-57970
