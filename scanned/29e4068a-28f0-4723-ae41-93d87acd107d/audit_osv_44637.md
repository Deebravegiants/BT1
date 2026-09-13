# [H] CRMEB through 6.0.0 Missing Authorization via Inert verifyAuth Role Check

## Summary
Severity: High
Advisory: CVE-2026-85212
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85212
Type: osv

## Details
CRMEB contains an authentication bypass vulnerability in the verifyAuth() method of SystemRoleServices.php that returns true from both conditional branches. Sub-administrators and accounts with no roles can access restricted admin endpoints by exploiting the inert role check that always permits requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85212.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85212
- https://www.vulncheck.com/advisories/crmeb-through-6.0.0-missing-authorization-via-inert-verifyauth-role-check
- https://github.com/crmeb/CRMEB/issues/119
- https://github.com/crmeb/CRMEB
- https://github.com/crmeb/CRMEB/blob/v6.0.0/crmeb/app/services/system/admin/SystemRoleServices.php
