# [M] JLSEC-2026-448

## Summary
Severity: Medium
Advisory: JLSEC-2026-448
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/JLSEC-2026-448
Type: osv

## Affected
- Julia: `Ncurses_jll` — affected >=0 <6.2.0+0

## Details
Buffer Overflow vulnerability in `fmt_entry` function in `progs/dump_entry.c:1116` in ncurses 6.1 allows remote attackers to cause a denial of service via crafted command.

## References
- http://seclists.org/fulldisclosure/2023/Dec/10
- http://seclists.org/fulldisclosure/2023/Dec/11
- http://seclists.org/fulldisclosure/2023/Dec/9
- https://github.com/zjuchenyuan/fuzzpoc/blob/master/infotocap_poc4.md
- https://security.netapp.com/advisory/ntap-20231006-0005/
- https://support.apple.com/kb/HT214036
- https://support.apple.com/kb/HT214037
- https://support.apple.com/kb/HT214038
