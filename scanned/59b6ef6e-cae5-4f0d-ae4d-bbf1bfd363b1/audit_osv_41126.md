# [H] ruoyi-vue-pro - Incorrect Permission Namespace in ErpSaleOrderController

## Summary
Severity: High
Advisory: CVE-2026-57950
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57950
Type: osv

## Details
ruoyi-vue-pro through 2026.05, fixed in commit 5d1fd70 contains a broken access control vulnerability in ErpSaleOrderController that allows attackers with erp:sale-out permissions to gain unauthorized access to sale order operations by exploiting an incorrect permission namespace enforcement. Attackers holding shipment-level permissions can perform unauthorized create, update, delete, and read operations on financially sensitive sale orders due to the controller enforcing erp:sale-out instead of the intended erp:sale-order namespace.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57950.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57950
- https://www.vulncheck.com/advisories/ruoyi-vue-pro-incorrect-permission-namespace-in-erpsaleordercontroller
- https://github.com/YunaiV/ruoyi-vue-pro/issues/1161
- https://github.com/YunaiV/ruoyi-vue-pro/commit/5d1fd70dc3e61bf64e7ce3328a71cc60001175c6
- https://github.com/YunaiV/ruoyi-vue-pro
