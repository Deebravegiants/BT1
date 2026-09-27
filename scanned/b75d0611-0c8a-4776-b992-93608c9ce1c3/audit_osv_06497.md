# [H] BIT-mariadb-2022-24051

## Summary
Severity: High
Advisory: BIT-mariadb-2022-24051
Aliases: BIT-mariadb-min-2022-24051, BIT-mysql-client-2022-24051, CVE-2022-24051
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-24051
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.8.0 <10.8.1

## Details
MariaDB CONNECT Storage Engine Format String Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of MariaDB. Authentication is required to exploit this vulnerability. The specific flaw exists within the processing of SQL queries. The issue results from the lack of proper validation of a user-supplied string before using it as a format specifier. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of the service account. Was ZDI-CAN-16193.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKJRBYJAQCOPHSED43A3HUPNKQLDTFGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZFZVMJL5UDTOZMARLXQIMG3BTG6UNYW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NJ4KDAGF3H4D4BDTHRAM6ZEAJJWWMRUO/
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220318-0004/
- https://www.zerodayinitiative.com/advisories/ZDI-22-318/
- https://nvd.nist.gov/vuln/detail/CVE-2022-24051
