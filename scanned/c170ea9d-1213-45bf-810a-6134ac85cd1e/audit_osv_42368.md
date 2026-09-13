# [H] Vendure 3.7.1 Cross-Channel Authorization Bypass via StockLocation and Asset Update

## Summary
Severity: High
Advisory: CVE-2026-67347
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67347
Type: osv

## Details
Vendure through 3.7.1, fixed in commit f67ef5f, contains a cross-channel authorization bypass vulnerability in stock-location.service.ts and asset.service.ts update methods that allows channel-scoped administrators to modify other tenants' data. Attackers can supply global IDs of StockLocation or Asset entities from different channels to overwrite inventory locations or catalog assets belonging to other tenants without proper channel isolation validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67347.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67347
- https://www.vulncheck.com/advisories/vendure-cross-channel-authorization-bypass-via-stocklocation-and-asset-update
- https://github.com/vendurehq/vendure/issues/5003
- https://github.com/vendurehq/vendure/commit/f67ef5f621282b785a2708df468bc6d2b8d8115b
- https://github.com/vendurehq/vendure/pull/5017
- https://github.com/vendurehq/vendure
