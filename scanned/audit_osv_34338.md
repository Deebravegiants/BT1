# [H] ERP: Possibility of SQL injection due to missing validation

## Summary
Severity: High
Advisory: CVE-2025-58439
Aliases: GHSA-fvjw-5w9q-6v39
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-06
Source: https://osv.dev/vulnerability/CVE-2025-58439
Type: osv

## Details
ERP is a free and open source Enterprise Resource Planning tool. In versions below 14.89.2 and 15.0.0 through 15.75.1, lack of validation of parameters left certain endpoints vulnerable to error-based SQL Injection. Some information like version could be retrieved. This issue is fixed in versions 14.89.2 and 15.76.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58439.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-fvjw-5w9q-6v39
- https://nvd.nist.gov/vuln/detail/CVE-2025-58439
- https://github.com/frappe/erpnext/pull/49219
- https://github.com/frappe/erpnext/pull/49220
