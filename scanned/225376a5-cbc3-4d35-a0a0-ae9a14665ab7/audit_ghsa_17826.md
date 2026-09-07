# [M] pimcore/customer-data-framework vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-q53r-9hh9-w277
CVE: CVE-2024-11956
CWE: CWE-564
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-q53r-9hh9-w277
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <4.2.1

## Details
An SQL injection vulnerability allows any authenticated user to execute arbitrary SQL commands on the server. This can lead to unauthorized access to sensitive data, data modification, or even complete control over the server.

Details
The vulnerability is found in the URL parameters of the following endpoint:

`GET /admin/customermanagementframework/customers/list?add-new-customer=1&apply-segment-selection=Apply&filterDefinition[allowedRoleIds][]=1&filterDefinition[allowedUserIds][]=2&filterDefinition[id]=0&filterDefinition[name]=RDFYjolf&filterDefinition[readOnly]=on&filterDefinition[shortcutAvailable]=on&filter[active]=1&filter[email]=testing%40example.com&filter[firstname]=RDFYjolf&filter[id]=1&filter[lastname]=RDFYjolf&filter[operator-customer]=AND&filter[operator-segments]=%40%40dz1Uu&filter[search]=the&filter[segments][832][]=847&filter[segments][833][]=835&filter[segments][874][]=876&filter[showSegments][]=832 HTTP/1.1`

The parameters filterDefinition and filter are vulnerable to SQL injection. When a specially crafted input is provided, it results in an SQL error, indicating that the input is being directly used in an SQL query without proper sanitization.

PoC
To reproduce the vulnerability, follow these steps:

Open a web browser or a tool like curl or Postman.
Authenticate with valid user credentials.
Navigate to the following URL with the vulnerable parameters:
```
https://demo.pimcore.fun/admin/customermanagementframework/customers/list?add-new-customer=1&apply-segment-selection=Apply&filterDefinition[allowedRoleIds][]=1&filterDefinition[allowedUserIds][]=2&filterDefinition[id]=0&filterDefinition[name]=RDFYjolf&filterDefinition[readOnly]=on&filterDefinition[shortcutAvailable]=on&filter[active]=1&filter[email]=testing%40example.com&filter[firstname]=RDFYjolf&filter[id]=1&filter[lastname]=RDFYjolf&filter[operator-customer]=AND&filter[operator-segments]=%40%40dz1Uu&filter[search]=the&filter[segments][832][]=847&filter[segments][833][]=835&filter[segments][874][]=876&filter[showSegments][]=832
Observe the error message indicating an SQL error:
Error while building customer list: An exception occurred while executing a query: SQLSTATE[42000]: Syntax error or access violation: 1064 You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near '@_0 ON `fltr_seg_832_0_@_0`.fieldname IN ('manualSegments','calculatedSegment...' at line 1
```
Impact
This is an SQL injection vulnerability. It impacts any authenticated user who can access the affected endpoint. An attacker can exploit this vulnerability to execute arbitrary SQL commands, potentially leading to data breaches, data loss, or full server compromise.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-q53r-9hh9-w277
- https://nvd.nist.gov/vuln/detail/CVE-2024-11956
- https://github.com/pimcore/customer-data-framework/releases/tag/v4.2.1
- https://github.com/pimcore/pimcore
- https://vuldb.com/?ctiid.293906
- https://vuldb.com/?id.293906
- https://vuldb.com/?submit.451863
