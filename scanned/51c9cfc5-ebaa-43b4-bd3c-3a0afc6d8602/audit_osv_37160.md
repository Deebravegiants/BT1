# [C] CouchCMS Privilege Escalation via f_k_levels_list Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-29002
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-29002
Type: osv

## Details
CouchCMS contains a privilege escalation vulnerability that allows authenticated Admin-level users to create SuperAdmin accounts by tampering with the f_k_levels_list parameter in user creation requests. Attackers can modify the parameter value from 4 to 10 in the HTTP request body to bypass authorization validation and gain full application control, circumventing restrictions on SuperAdmin account creation and privilege assignment.

## References
- https://www.couchcms.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29002
- https://www.vulncheck.com/advisories/couchcms-privilege-escalation-via-f-k-levels-list-parameter
- https://github.com/CouchCMS/CouchCMS
- https://gist.github.com/thepiyushkumarshukla/477e2d2bbbe8cc3ec0d640c50f0cf9e1
