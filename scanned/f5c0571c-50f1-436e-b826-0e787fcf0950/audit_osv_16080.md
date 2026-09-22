# [H] CVE-2019-25497

## Summary
Severity: High
Advisory: CVE-2019-25497
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2019-25497
Type: osv

## Details
osCommerce 2.3.4.1 contains a SQL injection vulnerability that allows unauthenticated attackers to manipulate database queries by injecting SQL code through the currency parameter. Attackers can send GET requests to shopping_cart.php with malicious currency values using boolean-based SQL injection payloads to extract sensitive database information.

## References
- https://www.oscommerce.com
- https://www.vulncheck.com/advisories/oscommerce-sql-injection-via-currency-parameter
- https://www.exploit-db.com/exploits/46328
