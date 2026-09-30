# [H] ALPINE-CVE-2020-9308

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-9308
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-9308
Type: osv

## Affected
- Alpine:v3.11: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.12: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.13: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.14: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.15: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.16: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.17: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.18: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.19: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.20: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.21: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.22: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.23: `libarchive` — affected >=3.4.0 <3.4.2-r0
- Alpine:v3.24: `libarchive` — affected >=3.4.0 <3.4.2-r0

## Details
archive_read_support_format_rar5.c in libarchive before 3.4.2 attempts to unpack a RAR5 file with an invalid or corrupted header (such as a header size of zero), leading to a SIGSEGV or possibly unspecified other impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-9308
