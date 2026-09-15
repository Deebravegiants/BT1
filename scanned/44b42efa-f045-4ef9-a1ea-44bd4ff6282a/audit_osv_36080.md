# [H] IDOR in Prospero Flow CRM allows cross-tenant payroll disclosure and creation

## Summary
Severity: High
Advisory: CVE-2026-19870
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-19870
Type: osv

## Details
Authorization Bypass Through User-Controlled Key in the payroll module in Roskus Prospero Flow CRM before 5.15.10 allows authenticated users holding the read payroll permission to view the salary and banking details of employees of any other company in the instance, and users holding the create payroll permission to create payroll records attributed to another company's employees, because the listing query is not scoped to the caller's company and the employee identifier is validated for global existence rather than company membership

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19870.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19870
- https://github.com/Roskus/prospero-flow-crm/commit/59644f910b7d1aec7d1ac962b0354b3ec209977e
- https://github.com/Roskus/prospero-flow-crm
- https://secur0.com/en/cna/cve-list/cve-2026-19870-idor-in-prospero-flow-crm-allows-cross-tenant-payroll-disclosure-and-creation
