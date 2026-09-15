# [H] CVE-2017-7484

## Summary
Severity: High
Advisory: CVE-2017-7484
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-7484
Type: osv

## Details
It was found that some selectivity estimation functions in PostgreSQL before 9.2.21, 9.3.x before 9.3.17, 9.4.x before 9.4.12, 9.5.x before 9.5.7, and 9.6.x before 9.6.3 did not check user privileges before providing information from pg_statistic, possibly leaking information. An unprivileged attacker could use this flaw to steal some information from tables they are otherwise not allowed to access.

## References
- http://www.securitytracker.com/id/1038476
- https://access.redhat.com/errata/RHSA-2017:2425
- https://security.gentoo.org/glsa/201710-06
- http://www.debian.org/security/2017/dsa-3851
- http://www.securityfocus.com/bid/98459
- https://access.redhat.com/errata/RHSA-2017:1677
- https://access.redhat.com/errata/RHSA-2017:1678
- https://access.redhat.com/errata/RHSA-2017:1838
- https://access.redhat.com/errata/RHSA-2017:1983
- https://www.postgresql.org/about/news/1746/
