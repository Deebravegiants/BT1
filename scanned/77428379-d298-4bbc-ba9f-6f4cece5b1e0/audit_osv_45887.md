# [M] JLSEC-2026-443

## Summary
Severity: Medium
Advisory: JLSEC-2026-443
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/JLSEC-2026-443
Type: osv

## Affected
- Julia: `Ncurses_jll` — affected >=0 <6.2.0+0

## Details
There is a heap-based buffer over-read in the `_nc_find_entry` function in `tinfo/comp_hash.c` in the terminfo library in ncurses before 6.1-20191012.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00061.html
- https://lists.gnu.org/archive/html/bug-ncurses/2019-10/msg00017.html
- https://lists.gnu.org/archive/html/bug-ncurses/2019-10/msg00045.html
- https://security.gentoo.org/glsa/202101-28
