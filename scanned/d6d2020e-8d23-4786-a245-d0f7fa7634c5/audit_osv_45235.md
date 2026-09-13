# [H] `execute_filter_audio` in `archive_read_support_format_rar.c` in libarchive before 3.7.5 allows...

## Summary
Severity: High
Advisory: JLSEC-2025-240
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-240
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=3.7.4+0 <3.7.9+0

## Details
`execute_filter_audio` in `archive_read_support_format_rar.c` in libarchive before 3.7.5 allows out-of-bounds access via a crafted archive file because src can move beyond dst.

## References
- https://github.com/libarchive/libarchive/compare/v3.7.4...v3.7.5
- https://github.com/libarchive/libarchive/pull/2149
- https://github.com/terrynini/CVE-Reports/blob/main/CVE-2024-48957/README.md
