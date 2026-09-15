# [M] BIT-sqlite-2021-20227

## Summary
Severity: Medium
Advisory: BIT-sqlite-2021-20227
Aliases: CVE-2021-20227
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sqlite-2021-20227
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.33.0 <3.34.1

## Details
A flaw was found in SQLite's SELECT query functionality (src/select.c). This flaw allows an attacker who is capable of running SQL queries locally on the SQLite database to cause a denial of service or possible code execution by triggering a use-after-free. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1924886
- https://security.gentoo.org/glsa/202103-04
- https://security.gentoo.org/glsa/202210-40
- https://security.netapp.com/advisory/ntap-20210423-0010/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.sqlite.org/releaselog/3_34_1.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-20227
