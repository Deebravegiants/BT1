# [M] CVE-2025-52048

## Summary
Severity: Medium
Advisory: CVE-2025-52048
Aliases: CVE-2025-58375, GHSA-mggw-6xqj-rphj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-52048
Type: osv

## Details
In Frappe 15.x.x before 15.72.0 and 14.x.x before 14.96.10, in the function add_tag() at `frappe/desk/doctype/tag/tag.py` is vulnerable to SQL Injection, which allows an attacker to extract information from databases by injecting a SQL query into the `dt` parameter.

## References
- https://github.com/Vietsunshine-Electronic-Solution-JSC/Vulnerability-Disclosures/blob/main/2025/Frappe%20Framework%20-%20Multiple%20SQL%20Injection.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52048.json
- https://github.com/frappe/frappe/security/advisories/GHSA-mggw-6xqj-rphj
- https://nvd.nist.gov/vuln/detail/CVE-2025-52048
