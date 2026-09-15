# [H] CVE-2019-25496

## Summary
Severity: High
Advisory: CVE-2019-25496
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2019-25496
Type: osv

## Details
osCommerce 2.3.4.1 contains a SQL injection vulnerability that allows unauthenticated attackers to manipulate database queries by injecting SQL code through the products_id parameter. Attackers can modify the products_id value in product_info.php requests and append boolean-based SQL injection payloads to extract sensitive database information.

## References
- https://www.oscommerce.com
- https://www.vulncheck.com/advisories/oscommerce-sql-injection-via-productsid-parameter
- https://www.exploit-db.com/exploits/46329
