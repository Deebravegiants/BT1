# [H] JLSEC-2026-28

## Summary
Severity: High
Advisory: JLSEC-2026-28
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-28
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
A flaw was found in the psql interactive terminal of PostgreSQL in versions before 13.1, before 12.5, before 11.10, before 10.15, before 9.6.20 and before 9.5.24. If an interactive psql session uses `\gset` when querying a compromised server, the attacker can execute arbitrary code as the operating system account running psql. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894430
- https://lists.debian.org/debian-lts-announce/2020/12/msg00005.html
- https://security.gentoo.org/glsa/202012-07
- https://www.postgresql.org/about/news/postgresql-131-125-1110-1015-9620-and-9524-released-2111/
