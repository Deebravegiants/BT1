# [H] ALPINE-CVE-2024-48958

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-48958
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-48958
Type: osv

## Affected
- Alpine:v3.21: `libarchive` — affected >=3.6.0 <3.7.5-r0
- Alpine:v3.22: `libarchive` — affected >=3.6.0 <3.7.5-r0
- Alpine:v3.23: `libarchive` — affected >=3.6.0 <3.7.5-r0
- Alpine:v3.24: `libarchive` — affected >=3.6.0 <3.7.5-r0

## Details
execute_filter_delta in archive_read_support_format_rar.c in libarchive before 3.7.5 allows out-of-bounds access via a crafted archive file because src can move beyond dst.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-48958
