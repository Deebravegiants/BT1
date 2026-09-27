# [H] JLSEC-2026-29

## Summary
Severity: High
Advisory: JLSEC-2026-29
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-29
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
When the server is configured to use trust authentication with a clientcert requirement or to use cert authentication, a man-in-the-middle attacker can inject arbitrary SQL queries when a connection is first established, despite the use of SSL certificate verification and encryption.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2022666
- https://git.postgresql.org/gitweb/?p=postgresql.git%3Ba=commit%3Bh=28e24125541545483093819efae9bca603441951
- https://github.com/postgres/postgres/commit/28e24125541545483093819efae9bca603441951
- https://security.gentoo.org/glsa/202211-04
- https://www.postgresql.org/support/security/CVE-2021-23214/
