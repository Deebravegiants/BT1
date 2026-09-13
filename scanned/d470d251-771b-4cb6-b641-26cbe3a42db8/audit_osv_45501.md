# [H] ncurses v6.5 and v6.4 are vulnerable to Buffer Overflow in progs/infocmp.c, function...

## Summary
Severity: High
Advisory: JLSEC-2026-1242
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/JLSEC-2026-1242
Type: osv

## Affected
- Julia: `Ncurses_jll` — affected >=0 <6.6.0+0

## Details
The infocmp command-line tool in ncurses before 6.5-20251213 has a stack-based buffer overflow in `analyze_string` in `progs/infocmp.c`.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://github.com/Cao-Wuhui/CVE-2025-69720
- https://github.com/advisories/GHSA-9952-mrqj-h4jh
- https://invisible-island.net/archives/ncurses/6.5
- https://invisible-island.net/archives/ncurses/6.5/
- https://invisible-island.net/ncurses
- https://invisible-island.net/ncurses/
- https://marc.info/?l=ncurses-bug&m=176539968328570&w=2
- https://marc.info/?l=ncurses-bug&m=176540731801330&w=2
- https://marc.info/?l=ncurses-bug&m=176545557728083&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2025-69720
