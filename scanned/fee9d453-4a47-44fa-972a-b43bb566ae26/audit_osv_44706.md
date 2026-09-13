# [M] Snipe-IT before 8.6.2 Authorization Bypass via Checkout-Acceptance

## Summary
Severity: Medium
Advisory: CVE-2026-85616
Aliases: GHSA-jqgw-vpjc-86fc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:L)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85616
Type: osv

## Details
Snipe-IT versions before 8.6.2 contain an authorization bypass vulnerability in checkout-acceptance report actions when Full Multiple Company Support is enabled. Authenticated users with reports.view permission can enumerate sequential acceptance IDs and soft-delete or trigger reminder emails for acceptances belonging to other companies by exploiting a null check on the legacy users.company_id column.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85616.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-jqgw-vpjc-86fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-85616
- https://www.vulncheck.com/advisories/snipe-it-before-8.6.2-authorization-bypass-via-checkout-acceptance
