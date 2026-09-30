# [H] WeKan < 8.35 Missing Authorization via Integration REST API

## Summary
Severity: High
Advisory: CVE-2026-41454
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41454
Type: osv

## Details
WeKan before 8.35 contains a missing authorization vulnerability in the Integration REST API endpoints that allows authenticated board members to perform administrative actions without proper privilege verification. Attackers can enumerate integrations including webhook URLs, create new integrations, modify or delete existing integrations, and manage integration activities by exploiting insufficient authorization checks in the JsonRoutes REST handlers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41454.json
- https://github.com/wekan/wekan/releases/tag/v8.35
- https://nvd.nist.gov/vuln/detail/CVE-2026-41454
- https://www.vulncheck.com/advisories/wekan-missing-authorization-via-integration-rest-api
- https://github.com/wekan/wekan/commit/2cd702f48df2b8aef0e7381685f8e089986a18a4
- https://github.com/wekan/wekan
