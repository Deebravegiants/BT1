# [C] MISP: SQL injection via unvalidated ordering parameters in event and shadow attribute listings

## Summary
Severity: Critical
Advisory: CVE-2026-44381
Aliases: GHSA-4cxp-22wm-j6jr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44381
Type: osv

## Details
MISP is an open source threat intelligence and sharing platform. Prior to 2.5.37, a SQL injection vulnerability existed in the handling of user-controlled ordering parameters in the event and shadow attribute listing endpoints. The affected code accepted order or sort values from request parameters and incorporated them into database query ordering clauses without sufficient validation of the requested field name. An attacker with access to the affected endpoints could craft a malicious ordering parameter to manipulate the generated SQL query. Depending on database permissions and query context, this could potentially allow unauthorized access to data, modification of query behavior, or other database-level impact. This vulnerability is fixed in 2.5.37.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44381.json
- https://github.com/MISP/MISP/security/advisories/GHSA-4cxp-22wm-j6jr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44381
