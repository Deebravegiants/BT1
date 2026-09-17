# [H] JLSEC-2026-27

## Summary
Severity: High
Advisory: JLSEC-2026-27
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-27
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
A flaw was found in PostgreSQL versions before 13.1, before 12.5, before 11.10, before 10.15, before 9.6.20 and before 9.5.24. An attacker having permission to create non-temporary objects in at least one schema can execute arbitrary SQL functions under the identity of a superuser. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894425
- https://lists.debian.org/debian-lts-announce/2020/12/msg00005.html
- https://security.gentoo.org/glsa/202012-07
- https://security.netapp.com/advisory/ntap-20201202-0003/
- https://www.postgresql.org/support/security/
