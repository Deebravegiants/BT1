# [H] Null Pointer Dereference vulnerability in libarchive 3.7.6 and earlier when running program bsdtar...

## Summary
Severity: High
Advisory: JLSEC-2025-244
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-244
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.9+0

## Details
Null Pointer Dereference vulnerability in libarchive 3.7.6 and earlier when running program bsdtar in function `header_pax_extension` at `rchive_read_support_format_tar.c:1844:8`.

## References
- https://github.com/88Sanghy88/crash-test
- https://github.com/libarchive/libarchive/releases/download/v3.7.6/libarchive-3.7.6.tar.gz
