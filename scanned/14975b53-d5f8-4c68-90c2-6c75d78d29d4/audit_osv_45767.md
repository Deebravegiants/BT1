# [M] JLSEC-2026-30

## Summary
Severity: Medium
Advisory: JLSEC-2026-30
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-30
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
A man-in-the-middle attacker can inject false responses to the client's first few queries, despite the use of SSL certificate verification and encryption.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2022675
- https://git.postgresql.org/gitweb/?p=postgresql.git%3Ba=commitdiff%3Bh=d83cdfdca9d918bbbd6bb209139b94c954da7228
- https://github.com/postgres/postgres/commit/160c0258802d10b0600d7671b1bbea55d8e17d45
- https://security.gentoo.org/glsa/202211-04
- https://www.postgresql.org/support/security/CVE-2021-23222/
