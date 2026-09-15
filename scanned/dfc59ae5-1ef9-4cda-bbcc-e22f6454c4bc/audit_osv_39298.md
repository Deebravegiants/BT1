# [M] CubeCart: Authenticated SQL Injection via `sort[]` Parameter in Admin Orders Transactions Listing

## Summary
Severity: Medium
Advisory: CVE-2026-45054
Aliases: GHSA-rm2f-rpcq-6w9f
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-45054
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to 6.7.0, the admin orders-transactions listing page (admin.php?_g=orders&node=transactions) builds a raw ORDER BY SQL fragment from the attacker-controlled $_GET['sort'] array without column or direction validation. Both the column key and the direction value flow into the query string as bare SQL tokens, and the framework's sqlSafe() (mysqli escape_string) escapes only quote characters — none of which are required for ORDER BY injection. An authenticated administrator with the minimum CC_PERM_READ permission on orders can execute arbitrary SQL against the store database, including time-based blind extraction of admin password hashes, customer PII, and integrated payment-gateway credentials. This vulnerability is fixed in 6.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45054.json
- https://github.com/cubecart/v6/security/advisories/GHSA-rm2f-rpcq-6w9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-45054
