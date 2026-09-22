# [H] BIT-mariadb-2020-28912

## Summary
Severity: High
Advisory: BIT-mariadb-2020-28912
Aliases: BIT-mariadb-min-2020-28912, BIT-mysql-client-2020-28912, CVE-2020-28912
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2020-28912
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.7

## Details
With MariaDB running on Windows, when local clients connect to the server over named pipes, it's possible for an unprivileged user with an ability to run code on the server machine to intercept the named pipe connection and act as a man-in-the-middle, gaining access to all the data passed between the client and the server, and getting the ability to run SQL commands on behalf of the connected user. This occurs because of an incorrect security descriptor. This affects MariaDB Server before 10.1.48, 10.2.x before 10.2.35, 10.3.x before 10.3.26, 10.4.x before 10.4.16, and 10.5.x before 10.5.7. NOTE: this issue exists because certain details of the MariaDB CVE-2019-2503 fix did not comprehensively address attack variants against MariaDB. This situation is specific to MariaDB, and thus CVE-2020-28912 does NOT apply to other vendors that were originally affected by CVE-2019-2503.

## References
- https://hackerone.com/reports/1019891
- https://jira.mariadb.org/browse/MDEV-24040
- https://nvd.nist.gov/vuln/detail/CVE-2020-28912
