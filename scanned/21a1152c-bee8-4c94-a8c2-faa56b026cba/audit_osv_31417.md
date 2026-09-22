# [M] OpenSupports 4.11.0 — SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2025-10692
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-10692
Type: osv

## Details
The endpoint POST /api/staff/get-new-tickets concatenates the user-controlled parameter departmentId directly into the SQL WHERE clause without parameter binding. As a result, an authenticated staff user (level ≥ 1) can inject SQL to alter the filter logic, effectively bypassing department scoping and disclosing tickets beyond their intended access.This issue affects OpenSupports: 4.11.0.

## References
- https://fluidattacks.com/advisories/tito
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10692.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10692
- https://github.com/opensupports/opensupports
