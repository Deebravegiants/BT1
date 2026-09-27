# [H] Use after free vulnerability in gawk 5.4.0 and earlier

## Summary
Severity: High
Advisory: JLSEC-2026-785
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/JLSEC-2026-785
Type: osv

## Affected
- Julia: `gawk_jll` — affected >=0 <5.4.1+0

## Details
Use After Free vulnerability has been found in "io.c" program file of gawk (`do_getline_redir()` routine). This issue may lead to a crash. It affects gawk in versions 5.4.0 and below.

## References
- https://cert.pl/en/posts/2026/07/CVE-2026-40467
- https://cgit.git.savannah.gnu.org/cgit/gawk.git/commit/?id=a2d18c74109e41bec29a23098eba2e00057286d8
