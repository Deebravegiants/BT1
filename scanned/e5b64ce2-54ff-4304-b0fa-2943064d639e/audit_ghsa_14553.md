# [H] NotrinosERP vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-4pqp-69m3-f8pp
CVE: CVE-2023-24788
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-4pqp-69m3-f8pp
Type: github-advisory

## Affected
- Packagist: `notrinos/notrinos-erp` — affected >=0

## Details
NotrinosERP v0.7 was discovered to contain a SQL injection vulnerability via the OrderNumber parameter at `/NotrinosERP/sales/customer_delivery.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24788
- https://github.com/arvandy/CVE/blob/main/CVE-2023-24788/CVE-2023-24788.md
- https://github.com/arvandy/CVE/blob/main/CVE-2023-24788/CVE-2023-24788.py
- https://github.com/arvandy/CVE/blob/main/NotrinosERP/POC.md
- https://github.com/notrinos/NotrinosERP
- http://packetstormsecurity.com/files/171804/NotrinosERP-0.7-SQL-Injection.html
