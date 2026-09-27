# [M] CVE-2017-7485

## Summary
Severity: Medium
Advisory: CVE-2017-7485
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-7485
Type: osv

## Details
In PostgreSQL 9.3.x before 9.3.17, 9.4.x before 9.4.12, 9.5.x before 9.5.7, and 9.6.x before 9.6.3, it was found that the PGREQUIRESSL environment variable was no longer enforcing a SSL/TLS connection to a PostgreSQL server. An active Man-in-the-Middle attacker could use this flaw to strip the SSL/TLS protection from a connection between a client and a server.

## References
- http://www.securitytracker.com/id/1038476
- http://www.debian.org/security/2017/dsa-3851
- http://www.securityfocus.com/bid/98461
- https://access.redhat.com/errata/RHSA-2017:1838
- https://security.gentoo.org/glsa/201710-06
- https://www.postgresql.org/about/news/1746/
- https://access.redhat.com/errata/RHSA-2017:1677
- https://access.redhat.com/errata/RHSA-2017:1678
- https://access.redhat.com/errata/RHSA-2017:2425
