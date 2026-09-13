# [H] Improper Input Validation in Datomic

## Summary
Severity: High
Advisory: GHSA-9pf8-qqhm-7w64
CVE: CVE-2018-10054
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9pf8-qqhm-7w64
Type: github-advisory

## Affected
- Maven: `com.datomic:datomic-free` — affected >=0 <0.9.5697

## Details
H2 1.4.197, as used in Datomic before 0.9.5697 and other products, allows remote code execution because CREATE ALIAS can execute arbitrary Java code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10054
- https://github.com/h2database/h2database/issues/1225
- https://github.com/h2database/h2database/issues/1808#issuecomment-599203115
- https://github.com/h2database/h2database/issues/3099
- https://forum.datomic.com/t/important-security-update-0-9-5697/379
- https://lists.apache.org/thread.html/582d4165de6507b0be82d5a6f9a1ce392ec43a00c9fed32bacf7fe1e%40%3Cuser.ignite.apache.org%3E
- https://lists.apache.org/thread.html/582d4165de6507b0be82d5a6f9a1ce392ec43a00c9fed32bacf7fe1e@%3Cuser.ignite.apache.org%3E
- https://lists.apache.org/thread.html/r8aaf4ee16bbaf6204731d4770d96ebb34b258cd79b491f9cdd7f2540%40%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/r8aaf4ee16bbaf6204731d4770d96ebb34b258cd79b491f9cdd7f2540@%3Ccommits.nifi.apache.org%3E
- https://mthbernardes.github.io/rce/2018/03/14/abusing-h2-database-alias.html
- https://security.netapp.com/advisory/ntap-20240719-0003
- https://www.exploit-db.com/exploits/44422
- http://blog.datomic.com/2018/03/important-security-update.html
