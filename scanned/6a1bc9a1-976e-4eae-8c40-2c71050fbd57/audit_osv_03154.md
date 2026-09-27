# [M] ALPINE-CVE-2024-57970

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-57970
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-57970
Type: osv

## Affected
- Alpine:v3.18: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.19: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.20: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.21: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.22: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.23: `libarchive` — affected >=0 <3.7.9-r0
- Alpine:v3.24: `libarchive` — affected >=0 <3.7.9-r0

## Details
libarchive through 3.7.7 has a heap-based buffer over-read in header_gnu_longlink in archive_read_support_format_tar.c via a TAR archive because it mishandles truncation in the middle of a GNU long linkname.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-57970
