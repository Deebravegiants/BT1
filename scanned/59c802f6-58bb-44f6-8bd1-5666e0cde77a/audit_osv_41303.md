# [M] BloodHound Missing Authorization on Custom Node Management API

## Summary
Severity: Medium
Advisory: CVE-2026-59255
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-59255
Type: osv

## Details
BloodHound through 9.4.0, fixed in commit 8f79035, contains a missing authorization vulnerability in the custom-nodes API endpoints that allows any authenticated user to modify the global graph schema. Attackers with valid session tokens can create, update, or delete custom node types affecting all users and tenants by invoking unprotected POST, PUT, and DELETE operations on the custom-nodes endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59255.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59255
- https://www.vulncheck.com/advisories/bloodhound-missing-authorization-on-custom-node-management-api
- https://github.com/SpecterOps/BloodHound/pull/2989
- https://github.com/SpecterOps/BloodHound/commit/8f790351349fd87bcb04377aba84cba6495825b3
- https://github.com/SpecterOps/BloodHound
- https://github.com/SpecterOps/BloodHound/issues/2910
