# [H] JLSEC-2026-452

## Summary
Severity: High
Advisory: JLSEC-2026-452
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/JLSEC-2026-452
Type: osv

## Affected
- Julia: `Ncurses_jll` — affected >=0 <6.4.0+0

## Details
ncurses 6.3 before patch 20220416 has an out-of-bounds read and segmentation violation in `convert_strings` in `tinfo/read_entry.c` in the terminfo library.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://lists.debian.org/debian-lts-announce/2022/10/msg00037.html
- https://lists.gnu.org/archive/html/bug-ncurses/2022-04/msg00014.html
- https://lists.gnu.org/archive/html/bug-ncurses/2022-04/msg00016.html
- https://support.apple.com/kb/HT213488
