# [H] Frappe SQL Injection due to improper field sanitization

## Summary
Severity: High
Advisory: CVE-2026-31877
Aliases: GHSA-2c4m-999q-xhx4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31877
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 15.84.0 and 14.99.0, a specially crafted request made to a certain endpoint could result in SQL injection, allowing an attacker to extract information they wouldn't otherwise be able to. This vulnerability is fixed in 15.84.0 and 14.99.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31877.json
- https://github.com/frappe/frappe/security/advisories/GHSA-2c4m-999q-xhx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-31877
