# [C] SQL injection in jeecgboot

## Summary
Severity: Critical
Advisory: GHSA-rwhx-6hx7-pqc8
CVE: CVE-2023-40989
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-22
Source: https://github.com/advisories/GHSA-rwhx-6hx7-pqc8
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-common` — affected >=0 <3.6.0

## Details
SQL injection vulnerbility in jeecgboot jeecg-boot v 3.0, 3.5.3 that allows a remote attacker to execute arbitrary code via a crafted request to the `report/jeecgboot/jmreport/queryFieldBySql` component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40989
- https://github.com/jeecgboot/jeecg-boot/commit/473875a9d261780a3400cf6f8260ca441b768ed1
- https://github.com/jeecgboot/jeecg-boot/commit/56e81fbf7bce11d2762b691f5d965b2265be608
- https://github.com/jeecgboot/jeecg-boot/commit/87677df925e55e51233bf740433b30a751fc7705
- https://github.com/Zone1-Z/CVE-2023-40989/blob/main/CVE-2023-40989
- ttps://github.com/jeecgboot/jeecg-boot
