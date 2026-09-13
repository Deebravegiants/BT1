# [M] SQL injection in index_chart_data action

## Summary
Severity: Medium
Advisory: CVE-2024-31212
Aliases: GHSA-qx95-w566-73fw
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-31212
Type: osv

## Details
InstantCMS is a free and open source content management system. A SQL injection vulnerability affects instantcms v2.16.2 in which an attacker with administrative privileges can cause the application to execute unauthorized SQL code. The vulnerability exists in index_chart_data action, which receives an input from user and passes it unsanitized to the core model `filterFunc` function that further embeds this data in an SQL statement. This allows attackers to inject unwanted SQL code into the statement. The `period` should be escaped before inserting it in the query. As of time of publication, a patched version is not available.

## References
- https://github.com/instantsoft/icms2/blob/4691a1524780e74107f6009b48d91e17a81b0fa1/system/controllers/admin/actions/index_chart_data.php#L190
- https://github.com/instantsoft/icms2/blob/4691a1524780e74107f6009b48d91e17a81b0fa1/system/core/model.php#L744
- https://user-images.githubusercontent.com/109034767/300806111-a33d9548-d99f-4034-bef3-fbd7fa62c37f.png
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31212.json
- https://github.com/instantsoft/icms2/security/advisories/GHSA-qx95-w566-73fw
- https://nvd.nist.gov/vuln/detail/CVE-2024-31212
