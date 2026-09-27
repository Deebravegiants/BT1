# [M] ruoyi-vue-pro - Missing Authorization in CRM Follow-up Record GET Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-57949
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57949
Type: osv

## Details
ruoyi-vue-pro through 2026.05, fixed in commit c779a47, contains a missing authorization vulnerability in the CRM module's GET /admin-api/crm/follow-up-record/get endpoint that allows authenticated users to read any follow-up record by iterating sequential numeric IDs. Attackers can exploit this by sending requests with arbitrary ID parameters to access other users' follow-up notes, file attachments, scheduling information, and business entity references without proper authorization checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57949.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57949
- https://www.vulncheck.com/advisories/ruoyi-vue-pro-missing-authorization-in-crm-follow-up-record-get-endpoint
- https://github.com/YunaiV/ruoyi-vue-pro/issues/1159
- https://github.com/YunaiV/ruoyi-vue-pro/commit/c779a476617c58a38904191094d22df254b42542
- https://github.com/YunaiV/ruoyi-vue-pro
