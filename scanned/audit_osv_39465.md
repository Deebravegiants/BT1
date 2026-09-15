# [C] Vvveb: Authenticated SQL injection in /user/orders via order_by and direction

## Summary
Severity: Critical
Advisory: CVE-2026-45800
Aliases: GHSA-vwcx-w4fq-9769
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45800
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.3, there is an authenticated SQL injection issue in the frontend user order history page in Vvveb CMS. A normal frontend user can log in and access /user/orders. The order_by and direction request parameters are accepted from the URL, propagated through the Orders component, and directly concatenated into the SQL ORDER BY clause in OrderSQL::getAll(). Because of this, attacker-controlled input reaches SQL structure without a whitelist or safe query construction step. This vulnerability is fixed in 1.0.8.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45800.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-vwcx-w4fq-9769
- https://nvd.nist.gov/vuln/detail/CVE-2026-45800
