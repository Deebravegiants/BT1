# [H] CVE-2015-4054

## Summary
Severity: High
Advisory: CVE-2015-4054
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2015-4054
Type: osv

## Details
PgBouncer before 1.5.5 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) by sending a password packet before a startup packet.

## References
- http://www.openwall.com/lists/oss-security/2015/05/22/5
- http://www.securityfocus.com/bid/74751
- https://github.com/pgbouncer/pgbouncer/commit/74d6e5f7de5ec736f71204b7b422af7380c19ac5
- https://github.com/pgbouncer/pgbouncer/commit/edab5be6665b9e8de66c25ba527509b229468573
- https://github.com/pgbouncer/pgbouncer/issues/42
- https://pgbouncer.github.io/changelog.html#pgbouncer-15x
- https://security.gentoo.org/glsa/201701-24
- http://www.openwall.com/lists/oss-security/2015/05/22/5
- https://github.com/pgbouncer/pgbouncer/issues/42
- https://github.com/pgbouncer/pgbouncer/commit/74d6e5f7de5ec736f71204b7b422af7380c19ac5
- https://github.com/pgbouncer/pgbouncer/commit/edab5be6665b9e8de66c25ba527509b229468573
