# [H] CVE-2019-25495

## Summary
Severity: High
Advisory: CVE-2019-25495
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2019-25495
Type: osv

## Details
osCommerce 2.3.4.1 contains a SQL injection vulnerability that allows unauthenticated attackers to manipulate database queries by injecting SQL code through the reviews_id parameter. Attackers can send GET requests to product_reviews_write.php with malicious reviews_id values using boolean-based SQL injection payloads to extract sensitive database information.

## References
- https://www.oscommerce.com
- https://www.vulncheck.com/advisories/oscommerce-sql-injection-via-reviewsid-parameter
- https://www.exploit-db.com/exploits/46330
