# [M] Possibility limited SQL injection due to insufficient validation in Frappe

## Summary
Severity: Medium
Advisory: CVE-2023-41328
Aliases: GHSA-53wh-f67g-9679
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-09-06
Source: https://osv.dev/vulnerability/CVE-2023-41328
Type: osv

## Details
Frappe is a low code web framework written in Python and Javascript. A SQL Injection vulnerability has been identified in the Frappe Framework which could allow a malicious actor to access sensitive information. This issue has been addressed in versions 13.46.1 and 14.20.0. Users are advised to upgrade. There's no workaround to fix this without upgrading.

## References
- https://github.com/frappe/frappe/releases/tag/v13.46.1
- https://github.com/frappe/frappe/releases/tag/v14.20.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41328.json
- https://github.com/frappe/frappe/security/advisories/GHSA-53wh-f67g-9679
- https://nvd.nist.gov/vuln/detail/CVE-2023-41328
