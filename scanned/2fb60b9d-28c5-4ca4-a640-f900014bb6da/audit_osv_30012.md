# [H] CVE-2024-48957

## Summary
Severity: High
Advisory: CVE-2024-48957
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/CVE-2024-48957
Type: osv

## Details
execute_filter_audio in archive_read_support_format_rar.c in libarchive before 3.7.5 allows out-of-bounds access via a crafted archive file because src can move beyond dst.

## References
- https://github.com/libarchive/libarchive/compare/v3.7.4...v3.7.5
- https://github.com/terrynini/CVE-Reports/blob/main/CVE-2024-48957/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48957.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48957
- https://github.com/libarchive/libarchive/pull/2149
