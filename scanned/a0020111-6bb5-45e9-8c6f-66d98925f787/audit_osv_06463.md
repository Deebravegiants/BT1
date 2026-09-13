# [C] BIT-mariadb-2020-15180

## Summary
Severity: Critical
Advisory: BIT-mariadb-2020-15180
Aliases: BIT-mariadb-min-2020-15180, BIT-mysql-client-2020-15180, CVE-2020-15180
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2020-15180
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.6

## Details
A flaw was found in the mysql-wsrep component of mariadb. Lack of input sanitization in `wsrep_sst_method` allows for command injection that can be exploited by a remote attacker to execute arbitrary commands on galera cluster nodes. This threatens the system's confidentiality, integrity, and availability. This flaw affects mariadb versions before 10.1.47, before 10.2.34, before 10.3.25, before 10.4.15 and before 10.5.6.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894919
- https://lists.debian.org/debian-lts-announce/2020/10/msg00021.html
- https://security.gentoo.org/glsa/202011-14
- https://www.debian.org/security/2020/dsa-4776
- https://www.percona.com/blog/2020/10/30/cve-2020-15180-affects-percona-xtradb-cluster/
- https://nvd.nist.gov/vuln/detail/CVE-2020-15180
