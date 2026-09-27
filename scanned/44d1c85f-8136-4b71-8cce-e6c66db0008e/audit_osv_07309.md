# [M] BIT-postgresql-2021-23222

## Summary
Severity: Medium
Advisory: BIT-postgresql-2021-23222
Aliases: CVE-2021-23222
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2021-23222
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=14.0.0 <14.0.1

## Details
A man-in-the-middle attacker can inject false responses to the client's first few queries, despite the use of SSL certificate verification and encryption.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2022675
- https://git.postgresql.org/gitweb/?p=postgresql.git%3Ba=commitdiff%3Bh=d83cdfdca9d918bbbd6bb209139b94c954da7228
- https://github.com/postgres/postgres/commit/160c0258802d10b0600d7671b1bbea55d8e17d45
- https://security.gentoo.org/glsa/202211-04
- https://www.postgresql.org/support/security/CVE-2021-23222/
- https://nvd.nist.gov/vuln/detail/CVE-2021-23222
