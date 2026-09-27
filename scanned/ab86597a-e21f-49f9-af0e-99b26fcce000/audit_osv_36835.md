# [H] EverShop has a Second-Order SQL Injection in URL Rewrite Processing Derived from Category URL Keys

## Summary
Severity: High
Advisory: CVE-2026-25993
Aliases: GHSA-3h84-9rhc-j2ch
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25993
Type: osv

## Details
EverShop is a TypeScript-first eCommerce platform. During category update and deletion event handling, the application embeds
path / request_path values—derived from the url_key stored in the database—into SQL statements via string concatenation and passes them to execute(). As a result, if a malicious string is stored in url_key , subsequent event processing modifies and executes the SQL statement, leading to a second-order SQL injection. Patched from v2.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25993.json
- https://github.com/evershopcommerce/evershop/security/advisories/GHSA-3h84-9rhc-j2ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-25993
- http://github.com/evershopcommerce/evershop/commit/5c5bdf2c1ad5d16ae68e9e48b494563953b6d1cd
