# [H] CVE-2017-7486

## Summary
Severity: High
Advisory: CVE-2017-7486
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-7486
Type: osv

## Details
PostgreSQL versions 8.4 - 9.6 are vulnerable to information leak in pg_user_mappings view which discloses foreign server passwords to any user having USAGE privilege on the associated foreign server.

## References
- http://www.securitytracker.com/id/1038476
- http://www.debian.org/security/2017/dsa-3851
- https://access.redhat.com/errata/RHSA-2017:1677
- https://access.redhat.com/errata/RHSA-2017:1983
- https://www.postgresql.org/about/news/1746/
- http://www.securityfocus.com/bid/98460
- https://access.redhat.com/errata/RHSA-2017:1678
- https://access.redhat.com/errata/RHSA-2017:1838
- https://access.redhat.com/errata/RHSA-2017:2425
- https://security.gentoo.org/glsa/201710-06
