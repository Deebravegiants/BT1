# [C] Krayin CRM Insecure Direct Object Reference via Controllers

## Summary
Severity: Critical
Advisory: CVE-2026-61460
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61460
Type: osv

## Details
Krayin CRM through 2.2.3 contains an insecure direct object reference vulnerability in LeadController, PersonController, OrganizationController, QuoteController, and ActivityController that allows authenticated users to edit, update, or delete records owned by other users. Attackers can modify CRM records and reassign ownership by exploiting missing record-level ownership validation in edit, update, and destroy methods.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61460.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-61460
- https://www.vulncheck.com/advisories/krayin-crm-insecure-direct-object-reference-via-controllers
- https://github.com/krayin/laravel-crm/pull/2567
- https://github.com/krayin/laravel-crm
- https://github.com/krayin/laravel-crm/issues/2559
